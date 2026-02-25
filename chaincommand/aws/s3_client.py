"""S3 operations for ChainCommand data persistence."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from ..config import settings
from ..utils.logging_config import get_logger

log = get_logger(__name__)


class S3Client:
    """Encapsulates S3 upload/download operations."""

    def __init__(
        self,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        import boto3

        self._bucket = bucket or settings.aws_s3_bucket
        self._prefix = (prefix or settings.aws_s3_prefix).rstrip("/")
        self._client = boto3.client("s3", region_name=region or settings.aws_region)

    def _build_key(self, table: str, filename: str) -> str:
        """Build a date-partitioned S3 key.

        Format: {prefix}/{table}/{year}/{month}/{day}/{filename}
        """
        now = datetime.now(timezone.utc)
        return (
            f"{self._prefix}/{table}"
            f"/{now.year:04d}/{now.month:02d}/{now.day:02d}"
            f"/{filename}"
        )

    def upload_dataframe(self, df: pd.DataFrame, key: str) -> str:
        """Upload a DataFrame as Parquet to S3."""
        buf = io.BytesIO()
        df.to_parquet(buf, index=False, engine="pyarrow")
        buf.seek(0)
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=buf.getvalue(),
            ContentType="application/octet-stream",
        )
        log.info("s3_upload_parquet", bucket=self._bucket, key=key, rows=len(df))
        return f"s3://{self._bucket}/{key}"

    def upload_jsonl(self, records: List[Dict[str, Any]], key: str) -> str:
        """Upload a list of dicts as JSONL to S3."""
        lines = "\n".join(json.dumps(r, default=str) for r in records)
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=lines.encode("utf-8"),
            ContentType="application/jsonl",
        )
        log.info("s3_upload_jsonl", bucket=self._bucket, key=key, records=len(records))
        return f"s3://{self._bucket}/{key}"

    def upload_json(self, data: Any, key: str) -> str:
        """Upload a single JSON object to S3."""
        body = json.dumps(data, default=str, indent=2)
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=body.encode("utf-8"),
            ContentType="application/json",
        )
        log.info("s3_upload_json", bucket=self._bucket, key=key)
        return f"s3://{self._bucket}/{key}"

    def list_objects(self, prefix: str) -> List[Dict[str, Any]]:
        """List objects under a given S3 prefix."""
        full_prefix = f"{self._prefix}/{prefix}"
        resp = self._client.list_objects_v2(Bucket=self._bucket, Prefix=full_prefix)
        contents = resp.get("Contents", [])
        return [
            {"key": obj["Key"], "size": obj["Size"], "last_modified": obj["LastModified"]}
            for obj in contents
        ]

    def download_json(self, key: str) -> Any:
        """Download and parse a JSON object from S3."""
        resp = self._client.get_object(Bucket=self._bucket, Key=key)
        body = resp["Body"].read().decode("utf-8")
        return json.loads(body)
