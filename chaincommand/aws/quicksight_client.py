"""QuickSight operations for ChainCommand dashboard creation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..config import settings
from ..utils.logging_config import get_logger

log = get_logger(__name__)

# ── Default dataset definitions ─────────────────────────

DEFAULT_DATASETS = [
    {
        "name": "KPI Trends",
        "description": "Historical KPI metrics from Redshift",
        "source_type": "redshift",
        "sql": (
            "SELECT cycle, timestamp, otif, fill_rate, mape, dsi, "
            "stockout_count, total_inventory_value, carrying_cost, "
            "order_cycle_time, perfect_order_rate, inventory_turnover, "
            "backorder_rate, supplier_defect_rate "
            "FROM kpi_snapshots ORDER BY cycle"
        ),
    },
    {
        "name": "Demand Patterns",
        "description": "Demand history analytics from Athena on S3",
        "source_type": "athena",
        "sql": (
            "SELECT date, product_id, quantity, is_promotion, day_of_week, month "
            "FROM demand_history ORDER BY date"
        ),
    },
    {
        "name": "Event Analytics",
        "description": "Supply chain event analytics from Athena on S3",
        "source_type": "athena",
        "sql": (
            "SELECT event_type, severity, source_agent, timestamp, description "
            "FROM events ORDER BY timestamp DESC"
        ),
    },
]


class QuickSightClient:
    """Encapsulates AWS QuickSight dataset and dashboard operations."""

    def __init__(
        self,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        import boto3

        self._account_id = account_id or settings.aws_quicksight_account_id
        self._client = boto3.client(
            "quicksight", region_name=region or settings.aws_region
        )

    def create_data_source(
        self, name: str, source_type: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a QuickSight data source (Athena or Redshift)."""
        ds_id = f"cc-{name.lower().replace(' ', '-')}-{uuid4().hex[:8]}"

        params: Dict[str, Any] = {}
        if source_type == "athena":
            params["AthenaParameters"] = {"WorkGroup": config.get("workgroup", "primary")}
        elif source_type == "redshift":
            params["RedshiftParameters"] = {
                "Host": config.get("host", settings.aws_redshift_host),
                "Port": config.get("port", settings.aws_redshift_port),
                "Database": config.get("database", settings.aws_redshift_db),
            }

        resp = self._client.create_data_source(
            AwsAccountId=self._account_id,
            DataSourceId=ds_id,
            Name=name,
            Type="ATHENA" if source_type == "athena" else "REDSHIFT",
            DataSourceParameters=params,
        )
        log.info("quicksight_data_source_created", name=name, ds_id=ds_id)
        return {"data_source_id": ds_id, "arn": resp.get("Arn", ""), "status": resp.get("CreationStatus", "")}

    def create_dataset(
        self, name: str, source_id: str, sql: str
    ) -> Dict[str, Any]:
        """Create a QuickSight dataset backed by a custom SQL query."""
        dataset_id = f"cc-ds-{name.lower().replace(' ', '-')}-{uuid4().hex[:8]}"

        resp = self._client.create_data_set(
            AwsAccountId=self._account_id,
            DataSetId=dataset_id,
            Name=name,
            PhysicalTableMap={
                "main": {
                    "CustomSql": {
                        "DataSourceArn": source_id,
                        "Name": name,
                        "SqlQuery": sql,
                    }
                }
            },
            ImportMode="DIRECT_QUERY",
        )
        log.info("quicksight_dataset_created", name=name, dataset_id=dataset_id)
        return {"dataset_id": dataset_id, "arn": resp.get("Arn", ""), "status": resp.get("Status", "")}

    def create_dashboard(
        self, name: str, dataset_ids: List[str]
    ) -> Dict[str, Any]:
        """Create a QuickSight dashboard from datasets (template-based)."""
        dashboard_id = f"cc-dash-{name.lower().replace(' ', '-')}-{uuid4().hex[:8]}"

        # Build dataset references
        dataset_refs = [
            {
                "DataSetPlaceholder": f"ds-{i}",
                "DataSetArn": ds_id,
            }
            for i, ds_id in enumerate(dataset_ids)
        ]

        resp = self._client.create_dashboard(
            AwsAccountId=self._account_id,
            DashboardId=dashboard_id,
            Name=name,
            SourceEntity={
                "SourceTemplate": {
                    "DataSetReferences": dataset_refs,
                    "Arn": f"arn:aws:quicksight:{settings.aws_region}:{self._account_id}:template/cc-default-template",
                }
            },
        )
        log.info("quicksight_dashboard_created", name=name, dashboard_id=dashboard_id)
        return {
            "dashboard_id": dashboard_id,
            "arn": resp.get("Arn", ""),
            "status": resp.get("CreationStatus", ""),
        }

    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all QuickSight dashboards in the account."""
        resp = self._client.list_dashboards(AwsAccountId=self._account_id)
        summaries = resp.get("DashboardSummaryList", [])
        return [
            {
                "dashboard_id": d.get("DashboardId", ""),
                "name": d.get("Name", ""),
                "arn": d.get("Arn", ""),
                "published_version": d.get("PublishedVersionNumber", 0),
                "last_updated": str(d.get("LastUpdatedTime", "")),
            }
            for d in summaries
        ]
