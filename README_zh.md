<div align="center">

# ChainCommand — 自主供應鏈優化 AI 團隊

**10 個 AI 代理 × 4 協作層 × 事件驅動架構：從數據到自主決策**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-E92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LLM Ready](https://img.shields.io/badge/LLM-Mock%20%7C%20OpenAI%20%7C%20Ollama-blueviolet.svg)](#llm-後端)

<br>

<img src="https://img.shields.io/badge/Agents-10%20Autonomous-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Architecture-Event%20Driven-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/ML%20Models-LSTM%20%2B%20XGBoost%20%2B%20GA%20%2B%20DQN-green?style=for-the-badge" />
<img src="https://img.shields.io/badge/API-REST%20%2B%20WebSocket-purple?style=for-the-badge" />
<img src="https://img.shields.io/badge/AWS-S3%20%7C%20Redshift%20%7C%20Athena%20%7C%20QuickSight-FF9900?style=for-the-badge" />
<img src="https://img.shields.io/badge/Tests-47%20Passed-brightgreen?style=for-the-badge" />

</div>

---

## 目錄

- [專案概述](#專案概述)
- [核心特色](#核心特色)
- [系統架構](#系統架構)
- [專案結構](#專案結構)
- [代理團隊](#代理團隊)
- [快速開始](#快速開始)
- [管線詳解](#管線詳解)
  - [Phase 1: LLM 抽象層](#phase-1-llm-抽象層)
  - [Phase 2: 代理工具](#phase-2-代理工具)
  - [Phase 3: ML 模型](#phase-3-ml-模型)
  - [Phase 4: KPI 引擎](#phase-4-kpi-引擎)
  - [Phase 5: 事件引擎](#phase-5-事件引擎)
  - [Phase 6: 代理團隊](#phase-6-代理團隊)
  - [Phase 7: API 層](#phase-7-api-層)
  - [Phase 8: 協調器](#phase-8-協調器)
- [API 參考](#api-參考)
- [決策週期演練](#決策週期演練)
- [研究基礎](#研究基礎)
- [AWS 整合（可選）](#aws-整合可選)
- [測試](#測試)
- [路線圖與未來工作](#路線圖與未來工作)
- [技術棧](#技術棧)
- [貢獻指南](#貢獻指南)
- [授權條款](#授權條款)
- [致謝](#致謝)

---

## 專案概述

**ChainCommand** 是一個多代理 AI 系統，能夠自主優化端到端供應鏈運營。十個專業代理——分佈在四個協作層（戰略層、戰術層、作業層、協調層）——透過非同步事件驅動 pub/sub 架構通訊，實現需求預測、庫存優化、供應風險評估、物流協調和執行報告生成。

整個系統僅需一條指令即可運行（`python -m chaincommand --demo`），無需任何 API 金鑰：自動生成真實供應鏈場景（50 個產品、20 個供應商、365 天需求歷史），訓練 ML 模型（LSTM + XGBoost 集成預測器、Isolation Forest 異常偵測器、GA + DQN 混合優化器），將 10 個代理與 16 個工具透過 EventBus 串接，並執行完整的 8 步決策週期——搭配 Rich 終端儀表板即時顯示進度、色彩 KPI 指標和代理層級結果。

### 為什麼建立這個專案？

| 挑戰 | 我們的方案 |
|------|-----------|
| 供應鏈決策各自為政 | 10 個專業代理搭配跨層事件通訊 |
| 預測依賴單一模型 | LSTM + XGBoost 集成搭配動態 MAPE 加權 |
| 庫存優化為靜態 | GA 全域搜索 + DQN 強化學習混合方案 |
| 高成本決策缺乏監督 | HITL（Human-In-The-Loop）閘門搭配可配置門檻 |
| 牛鞭效應放大波動 | 受啤酒遊戲研究啟發的跨代理共識機制 |
| 監控為被動式 | 主動監控引擎每個 tick 掃描異常和 KPI 違反 |

---

## 核心特色

- **10 代理自主團隊** — 需求預測、戰略規劃、庫存優化、供應商管理、物流協調、異常偵測、風險評估、市場情報、協調器（CSCO）、報告代理
- **4 層架構** — 戰略層（週/月）、戰術層（日）、作業層（即時）、協調層（跨層協調）——靈感來自京東兩層架構（ArXiv 2509.03811）
- **事件驅動通訊** — Pub/Sub EventBus 解耦代理互動；代理訂閱相關事件並自主反應
- **集成預測** — LSTM + XGBoost 動態反向 MAPE 加權，根據各模型準確度自動調整
- **混合優化** — 遺傳演算法（GA）全域參數搜索 + DQN 強化學習動態庫存決策
- **異常偵測** — Isolation Forest + Z-score 偵測需求突變、成本異常、前置時間偏差
- **HITL 審批閘門** — 訂單 ≥$50K 需人工審批（HIGH）；$10K–$50K 待人工審核（MEDIUM）；<$10K 自動批准；可透過環境變數配置
- **主動監控** — 持續的 tick 式掃描，偵測低庫存、KPI 違反、交貨延遲和異常
- **12 項 KPI 指標** — OTIF、滿足率、MAPE、DSI、缺貨次數、庫存周轉率、持有成本、完美訂單率、缺貨率、供應商缺陷率等
- **REST API + WebSocket** — 完整 FastAPI 儀表板，支援即時事件串流、代理觸發和模擬控制
- **Rich 終端 UI** — Demo 模式搭配動態進度條、色彩 KPI 儀表板、代理層級樹狀圖、嚴重度標記事件日誌和步驟耗時圖表（基於 `rich`）
- **Mock 優先設計** — 完整系統可在無 API 金鑰下運行，使用規則型 Mock LLM
- **AWS 持久化（可選）** — Strategy Pattern 後端，整合 S3、Redshift、Athena、QuickSight；未啟用時預設為零開銷 NullBackend
- **47 項單元測試** — AWS 後端完整測試覆蓋，使用 mocked boto3/redshift-connector（無需真實 AWS 憑證）

---

## 系統架構

```
              ┌──────────────────────────────────────────────────────────────────────┐
              │                    ChainCommand 架構                                 │
              └──────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │                         協調層 (ORCHESTRATION LAYER)                             │
  │  ┌──────────────────────┐    ┌──────────────────────┐                           │
  │  │   協調代理            │    │   報告代理            │                           │
  │  │   (CSCO — 衝突仲裁   │    │   (結構化報告         │                           │
  │  │    + HITL 閘門)       │    │    + 儀表板數據)       │                           │
  │  └──────────┬───────────┘    └──────────┬───────────┘                           │
  └─────────────┼───────────────────────────┼───────────────────────────────────────┘
                │          ▲                │          ▲
                ▼          │                ▼          │
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │                         戰略層 (STRATEGIC LAYER — 週/月)                         │
  │  ┌──────────────────────┐    ┌──────────────────────┐                           │
  │  │ 需求預測代理          │    │ 戰略規劃代理          │                           │
  │  │ (LSTM+XGB 集成)       │    │ (共識機制)            │                           │
  │  └──────────┬───────────┘    └──────────┬───────────┘                           │
  └─────────────┼───────────────────────────┼───────────────────────────────────────┘
                │          ▲                │          ▲
                ▼          │                ▼          │
  ┌──────────────────────────────────────────────────────────────────────────────────┐
  │                         戰術層 (TACTICAL LAYER — 日)                              │
  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │
  │  │ 庫存優化代理      │  │ 供應商管理代理    │  │ 物流協調代理      │               │
  │  │ (GA+DQN 混合)     │  │ (HITL 閘門)      │  │ (訂單追蹤)       │               │
  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘               │
  └───────────┼─────────────────────┼─────────────────────┼──────────────────────────┘
              │          ▲          │          ▲          │          ▲
              ▼          │          ▼          │          ▼          │
  ┌──────────────────────────────────────────────────────────────────────────────────┐
  │                         作業層 (OPERATIONAL LAYER — 即時)                         │
  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │
  │  │ 異常偵測代理      │  │ 風險評估代理      │  │ 市場情報代理      │               │
  │  │ (Isolation Forest)│  │ (深度/廣度/       │  │ (趨勢掃描)       │               │
  │  │                   │  │  關鍵性指標)      │  │                  │               │
  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘               │
  └───────────┼─────────────────────┼─────────────────────┼──────────────────────────┘
              │                     │                     │
              ▼                     ▼                     ▼
  ┌──────────────────────────────────────────────────────────────────────────────────┐
  │                              事件匯流排 (EVENT BUS — Pub/Sub)                    │
  │  forecast_updated │ reorder_triggered │ anomaly_detected │ po_created │ tick ... │
  └──────────────────────────────────────────────────────────────────────────────────┘
              │                     │                     │
              ▼                     ▼                     ▼
  ┌──────────────┐     ┌───────────────┐     ┌──────────────────┐
  │  KPI 引擎    │     │ 主動監控引擎  │     │  FastAPI 伺服器  │
  │  (12 指標)   │     │               │     │  (REST + WS)     │
  └──────────────┘     └───────────────┘     └──────────────────┘
```

---

## 專案結構

```
chaincommand/
│
├── __init__.py                          # 套件元數據 (v1.0.0)
├── __main__.py                          # CLI 入口 (--demo / server)
├── config.py                            # Pydantic Settings（環境變數驅動）
├── orchestrator.py                      # 系統協調器與運行時狀態
│
├── llm/                                 # LLM 抽象層
│   ├── __init__.py
│   ├── base.py                          # 抽象基類 (generate / generate_json)
│   ├── mock_llm.py                      # 規則型 Mock（正則表達式意圖匹配）
│   ├── openai_llm.py                    # OpenAI 非同步客戶端（JSON 模式）
│   ├── ollama_llm.py                    # Ollama 本地模型（httpx）
│   └── factory.py                       # 工廠：create_llm() 依據 CC_LLM_MODE
│
├── data/                                # 領域數據
│   ├── __init__.py
│   ├── schemas.py                       # 13 個 Pydantic 模型 + 4 個枚舉（Product, Supplier, PO, KPI 等）
│   └── generator.py                     # 合成數據：50 產品、20 供應商、365 天需求歷史
│
├── tools/                               # 代理工具（16 個工具）
│   ├── __init__.py
│   ├── base_tool.py                     # 抽象 BaseTool
│   ├── data_tools.py                    # QueryDemandHistory, QueryInventoryStatus 等
│   ├── forecast_tools.py               # RunDemandForecast, GetForecastAccuracy
│   ├── optimization_tools.py           # CalculateReorderPoint, OptimizeInventory, EvaluateSupplier
│   ├── risk_tools.py                    # DetectAnomalies, AssessSupplyRisk, ScanMarketIntelligence
│   └── action_tools.py                 # CreatePurchaseOrder, RequestHumanApproval, AdjustSafetyStock, EmitEvent
│
├── models/                              # ML 模型
│   ├── __init__.py
│   ├── forecaster.py                    # LSTMForecaster, XGBForecaster, EnsembleForecaster
│   ├── anomaly_detector.py             # AnomalyDetector（Isolation Forest + Z-score）
│   └── optimizer.py                     # GeneticOptimizer, DQNOptimizer, HybridOptimizer
│
├── kpi/                                 # KPI 引擎
│   ├── __init__.py
│   └── engine.py                        # KPIEngine（12 指標、閾值檢查、趨勢分析）
│
├── events/                              # 事件引擎
│   ├── __init__.py
│   ├── bus.py                           # EventBus（非同步 pub/sub）
│   └── monitor.py                       # ProactiveMonitor（tick 式健康檢查）
│
├── agents/                              # 代理團隊（10 個代理）
│   ├── __init__.py
│   ├── base_agent.py                    # BaseAgent（think / act / handle_event）
│   ├── demand_forecaster.py             # 戰略層：需求分析與預測
│   ├── strategic_planner.py             # 戰略層：庫存策略與共識機制
│   ├── inventory_optimizer.py           # 戰術層：再訂購點與安全庫存
│   ├── supplier_manager.py              # 戰術層：供應商評估與採購
│   ├── logistics_coordinator.py         # 戰術層：訂單追蹤與交貨管理
│   ├── anomaly_detector_agent.py        # 作業層：即時異常偵測
│   ├── risk_assessor.py                 # 作業層：供應風險量化
│   ├── market_intelligence.py           # 作業層：市場信號掃描
│   ├── coordinator.py                   # 協調層：CSCO 衝突解決
│   └── reporter.py                      # 協調層：結構化報告生成
│
├── api/                                 # FastAPI 應用
│   ├── __init__.py
│   ├── app.py                           # FastAPI 應用（CORS、生命週期管理）
│   └── routes/
│       ├── __init__.py
│       ├── dashboard.py                 # KPI、庫存、代理、事件、預測、審批、AWS、WebSocket
│       └── control.py                   # 模擬啟動/停止/速度、代理觸發
│
├── ui/                                  # Rich 終端 UI（Demo 模式）
│   ├── __init__.py
│   ├── theme.py                        # 視覺常數、顏色、層級標籤
│   └── console.py                      # ChainCommandUI（進度條、KPI 儀表板、樹狀圖）
│
├── aws/                                 # AWS 持久化後端（可選）
│   ├── __init__.py                      # 套件初始化，匯出 get_backend()
│   ├── config.py                        # AWS 配置輔助工具
│   ├── backend.py                       # PersistenceBackend ABC, NullBackend, 工廠
│   ├── aws_backend.py                   # AWSBackend — 組裝所有客戶端
│   ├── s3_client.py                     # S3 上傳/下載（Parquet, JSONL, JSON）
│   ├── redshift_client.py              # Redshift DDL, COPY, 查詢
│   ├── athena_client.py                # Athena 外部表、ad-hoc 查詢
│   └── quicksight_client.py            # QuickSight 數據集 + 儀表板
│
└── utils/                               # 工具程式
    ├── __init__.py
    └── logging_config.py               # structlog 配置

tests/                                       # 測試套件
├── __init__.py
├── test_agents/
├── test_api/
├── test_aws/                                # AWS 後端測試（全部 mocked）
│   ├── test_backend.py                      # NullBackend, get_backend(), AWSBackend
│   ├── test_s3_client.py                    # S3Client 操作
│   ├── test_redshift_client.py              # RedshiftClient DDL + 查詢
│   ├── test_athena_client.py                # AthenaClient 外部表 + 輪詢
│   └── test_quicksight_client.py            # QuickSightClient 數據集 + 儀表板
├── test_integration/
├── test_kpi/
└── test_models/
```

---

## 代理團隊

### 4 層 10 代理

| 層級 | 代理 | 角色 | 工具 | 事件訂閱 |
|------|------|------|------|---------|
| **戰略層** | 需求預測代理 | 分析銷售模式，產出需求預測 | QueryDemandHistory, RunDemandForecast, GetForecastAccuracy, ScanMarketIntelligence | `kpi_threshold_violated`, `new_market_intel` |
| **戰略層** | 戰略規劃代理 | 制定庫存策略，降低牛鞭效應 | QueryKPIHistory, OptimizeInventory, QueryInventoryStatus | `forecast_updated`, `kpi_trend_alert` |
| **戰術層** | 庫存優化代理 | 監控庫存水位，管理再訂購點 | QueryInventoryStatus, CalculateReorderPoint, AdjustSafetyStock, OptimizeInventory | `low_stock_alert`, `overstock_alert`, `stockout_alert`, `forecast_updated` |
| **戰術層** | 供應商管理代理 | 評估供應商、選擇最佳供應商、管理採購 | QuerySupplierInfo, EvaluateSupplier, CreatePurchaseOrder, RequestHumanApproval | `reorder_triggered`, `supplier_issue`, `quality_alert` |
| **戰術層** | 物流協調代理 | 追蹤出貨、管理交期 | QueryInventoryStatus, EmitEvent | `po_created`, `delivery_delayed` |
| **作業層** | 異常偵測代理 | 即時異常偵測（需求/成本/品質） | DetectAnomalies, QueryDemandHistory, QueryInventoryStatus | `new_data_point`, `tick` |
| **作業層** | 風險評估代理 | 量化供應風險（深度/廣度/關鍵性） | AssessSupplyRisk, ScanMarketIntelligence, QuerySupplierInfo | `anomaly_detected`, `supply_risk_alert` |
| **作業層** | 市場情報代理 | 監控市場動態、掃描趨勢 | ScanMarketIntelligence, EmitEvent | `tick` |
| **協調層** | 協調代理 (CSCO) | 解決衝突、強制約束、產出執行摘要 | 所有查詢工具, RequestHumanApproval, EmitEvent | **所有事件** |
| **協調層** | 報告代理 | 匯整輸出為結構化報告 | QueryKPIHistory, QueryInventoryStatus | `cycle_complete`, `kpi_snapshot_created` |

---

## 快速開始

### 系統需求

- Python 3.11 或更高版本
- pip 套件管理器

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/hsinnearth7/ChainCommand_Autonomous_Supply_Chain_Optimizer_Agent_Team.git
cd ChainCommand_Autonomous_Supply_Chain_Optimizer_Agent_Team

# 安裝依賴
pip install pydantic pydantic-settings numpy pandas structlog rich

# API 伺服器模式（可選）
pip install fastapi uvicorn

# AWS 持久化後端（可選）
pip install boto3 redshift-connector pyarrow

# 執行測試（可選）
pip install pytest pytest-asyncio
```

### 快速開始 — Demo 模式

```bash
# 執行單次決策週期（無需伺服器、無需 API 金鑰）
python -m chaincommand --demo
```

這將會：
1. 生成 50 個產品、20 個供應商、365 天需求歷史
2. 在 20 個產品上訓練 LSTM + XGBoost 集成預測器
3. 在全部 50 個產品上訓練 Isolation Forest 異常偵測器
4. 使用 Mock LLM 初始化 10 個 AI 代理
5. 執行一次完整的 8 步決策週期
6. 顯示 Rich 終端 UI，包含進度條、KPI 儀表板、代理樹狀圖和事件日誌

> **注意：** 安裝 `rich>=13.0.0` 以啟用增強終端 UI。若未安裝 `rich`，Demo 將自動降級為純文字輸出。

### Demo 截圖

**啟動與初始化**
![啟動與初始化](demo/demo_1_header_init.png)

**決策週期警報、步驟耗時與 KPI 儀表板**
![決策週期與 KPI](demo/demo_2_cycle_kpi.png)

**代理結果樹與事件日誌**
![代理與事件](demo/demo_3_agents_events.png)

### API 伺服器模式

```bash
# 啟動 FastAPI 伺服器（自動初始化系統）
python -m chaincommand

# 或指定主機/埠
python -m chaincommand --host 0.0.0.0 --port 8000
```

然後造訪：
- 儀表板：`http://localhost:8000/docs`（Swagger UI）
- KPI：`curl http://localhost:8000/api/kpi/current`
- 啟動模擬：`curl -X POST http://localhost:8000/api/simulation/start`

### 環境變數

所有設定可透過 `CC_` 前綴環境變數或 `.env` 檔案配置：

```bash
# LLM 後端 (mock | openai | ollama)
CC_LLM_MODE=mock

# OpenAI（當 CC_LLM_MODE=openai）
CC_OPENAI_API_KEY=sk-...
CC_OPENAI_MODEL=gpt-4o-mini

# Ollama（當 CC_LLM_MODE=ollama）
CC_OLLAMA_BASE_URL=http://localhost:11434
CC_OLLAMA_MODEL=llama3

# 模擬參數
CC_NUM_PRODUCTS=50
CC_NUM_SUPPLIERS=20
CC_SIMULATION_SPEED=1.0

# KPI 門檻
CC_OTIF_TARGET=0.95
CC_FILL_RATE_TARGET=0.97
CC_MAPE_THRESHOLD=15.0

# HITL 升級門檻
CC_COST_ESCALATION_THRESHOLD=50000
CC_AUTO_APPROVE_BELOW=10000
```

---

## 管線詳解

### Phase 1: LLM 抽象層

> `chaincommand/llm/` — 所有代理共用的統一 LLM 介面

所有代理透過 `BaseLLM` 通訊，提供兩種方法：

```python
async def generate(prompt, system, temperature) -> str          # 自由文字
async def generate_json(prompt, schema, system, temperature) -> BaseModel  # 結構化輸出
```

| 後端 | 類別 | 說明 |
|------|------|------|
| **Mock** | `MockLLM` | 正則表達式意圖匹配搭配預定義回應（無需 API 金鑰） |
| **OpenAI** | `OpenAILLM` | 非同步 OpenAI 客戶端，支援 JSON 模式 |
| **Ollama** | `OllamaLLM` | httpx 非同步客戶端，連接本地 Ollama 實例 |

工廠函數 `create_llm()` 根據 `CC_LLM_MODE` 實例化對應後端。

---

### Phase 2: 代理工具

> `chaincommand/tools/` — 代理可調用的 16 個工具

| 分類 | 工具 | 說明 |
|------|------|------|
| **數據查詢** | QueryDemandHistory, QueryInventoryStatus, QuerySupplierInfo, QueryKPIHistory | 唯讀存取系統狀態 |
| **預測** | RunDemandForecast, GetForecastAccuracy | 觸發集成預測並取得 MAPE 指標 |
| **優化** | CalculateReorderPoint, OptimizeInventory, EvaluateSupplier | 計算 ROP、執行 GA/DQN 優化、供應商評分 |
| **風險** | DetectAnomalies, AssessSupplyRisk, ScanMarketIntelligence | 異常偵測、多維風險評分、市場掃描 |
| **行動** | CreatePurchaseOrder, RequestHumanApproval, AdjustSafetyStock, EmitEvent | 寫入操作搭配 HITL 閘門 |

---

### Phase 3: ML 模型

> `chaincommand/models/` — 預測、異常偵測與優化

**集成預測器** — LSTM + XGBoost 動態加權：
```
Weight_LSTM = (1/MAPE_LSTM) / ((1/MAPE_LSTM) + (1/MAPE_XGB))
Weight_XGB  = (1/MAPE_XGB)  / ((1/MAPE_LSTM) + (1/MAPE_XGB))
```

**異常偵測器** — Isolation Forest + Z-score 備援：
- 需求突變偵測 (|z| > 2.5)
- 過剩庫存偵測 (DSI > 60 天)
- 不足庫存偵測 (DSI < 10 天)

**混合優化器** — GA 提供結構性參數，DQN 提供動態訂購決策：
```
GA  → reorder_point, safety_stock    (全域搜索，50 種群 × 100 世代)
DQN → order_quantity                  (動態策略，200 回合，ε-貪婪)
混合：60% GA + 40% DQN 訂購量加權
```

---

### Phase 4: KPI 引擎

> `chaincommand/kpi/engine.py` — 12 項即時供應鏈指標

| KPI | 公式 | 門檻 |
|-----|------|------|
| **OTIF** | 準時齊全交貨數 / 總交貨數 | ≥ 95% |
| **滿足率** | 已滿足需求 / 總需求 | ≥ 97% |
| **MAPE** | 預測平均絕對百分比誤差 | ≤ 15% |
| **DSI** | 總庫存 / 平均日需求 | 10–60 天 |
| **缺貨次數** | 零庫存產品數 | ≤ 3 |
| **庫存價值** | Σ (庫存 × 單位成本) | — |
| **持有成本** | 庫存價值的 25% / 365（日） | — |
| **訂單週期時間** | 從 PO 建立到交貨的平均天數 | — |
| **完美訂單率** | 完美交貨數 / 總訂單數 | — |
| **庫存周轉率** | 年度 COGS / 平均庫存價值 | — |
| **缺貨率** | 缺貨產品數 / 總產品數 | — |
| **供應商缺陷率** | 所有活躍供應商的平均缺陷率 | — |

---

### Phase 5: 事件引擎

> `chaincommand/events/` — 非同步 pub/sub 與主動監控

**EventBus** — 非同步發布/訂閱，具備錯誤隔離：
```
publish(event) → 分發至特定類型訂閱者 + 萬用訂閱者
subscribe(event_type, handler) → 註冊特定事件
subscribe_all(handler) → 註冊所有事件（協調代理使用）
```

**ProactiveMonitor** — Tick 式健康掃描：
1. 庫存水位檢查 → `stockout_alert`, `low_stock_alert`, `overstock_alert`
2. KPI 閾值違反 → `kpi_threshold_violated`
3. 交貨延遲偵測 → `delivery_delayed`
4. 異常偵測批次 → `anomaly_detected`
5. Tick 心跳 → `tick`（供每週期執行的代理使用）

---

### Phase 6: 代理團隊

> `chaincommand/agents/` — 10 個代理，think/act/handle_event 生命週期

每個代理遵循相同的生命週期：

```python
class BaseAgent(ABC):
    async def think(context) -> str           # LLM 推理
    async def act(action: AgentAction) -> dict # 工具執行
    async def handle_event(event)              # 反應式事件處理
    async def run_cycle(context) -> dict       # 完整決策週期
```

代理之間僅透過 EventBus 通訊——無直接代理對代理呼叫。此解耦設計帶來：
- 各代理可獨立擴展
- 故障隔離（一個代理的錯誤不會影響其他代理）
- 易於新增代理而無需修改現有代理

---

### Phase 7: API 層

> `chaincommand/api/` — FastAPI（REST + WebSocket）

詳見下方 [API 參考](#api-參考)。

---

### Phase 8: 協調器

> `chaincommand/orchestrator.py` — 系統協調器

協調器管理完整的生命週期：

```
initialize()  → 生成數據 → 訓練 ML 模型 → 建立代理 → 配置事件訂閱 → 初始化持久化後端
run_cycle()   → 8 步決策週期，跨所有代理層 → 將週期數據持久化至後端
run_loop()    → 持續模擬，可配置速度
shutdown()    → 清理持久化後端 → 停止監控器 → 停止事件匯流排
```

---

## API 參考

### 儀表板端點

| 方法 | 端點 | 說明 |
|------|------|------|
| `GET` | `/api/kpi/current` | 最新 KPI 快照（12 指標） |
| `GET` | `/api/kpi/history?periods=30` | KPI 趨勢數據 |
| `GET` | `/api/inventory/status` | 所有產品庫存狀態 |
| `GET` | `/api/inventory/status?product_id=PRD-0001` | 單一產品詳情 |
| `GET` | `/api/agents/status` | 全部 10 個代理狀態 |
| `GET` | `/api/events/recent?limit=50` | 最近供應鏈事件 |
| `GET` | `/api/forecast/{product_id}` | 30 天需求預測 |
| `GET` | `/api/approvals/pending` | 待處理 HITL 審批請求 |
| `POST` | `/api/approval/{id}/decide` | 批准或拒絕審批請求 |
| `GET` | `/api/aws/status` | AWS 後端狀態與配置 |
| `GET` | `/api/aws/kpi-trend/{metric}` | 從 Redshift 查詢 KPI 趨勢 |
| `GET` | `/api/aws/query` | 透過 Athena 的 ad-hoc 事件查詢 |
| `GET` | `/api/aws/dashboards` | 列出 QuickSight 儀表板 |
| `WS` | `/ws/live` | 即時事件串流 |

### 控制端點

| 方法 | 端點 | 說明 |
|------|------|------|
| `POST` | `/api/simulation/start` | 啟動持續模擬迴圈 |
| `POST` | `/api/simulation/stop` | 停止模擬 |
| `POST` | `/api/simulation/speed?speed=5.0` | 調整模擬速度（0.1–100 倍） |
| `POST` | `/api/agents/{name}/trigger` | 手動觸發單一代理週期 |
| `GET` | `/api/simulation/status` | 運行狀態、週期數、統計數據 |

---

## 決策週期演練

每個週期遵循 8 步序列，對應真實供應鏈決策流程：

```
步驟 1: 作業層掃描
  ├── 市場情報代理  → 掃描 3 個市場信號（價格、法規、競爭者）
  └── 異常偵測代理  → 掃描 50 個產品的需求/成本/庫存異常
                       （Demo 運行中偵測到 82 個異常）

步驟 2: 戰略預測
  └── 需求預測代理  → LSTM+XGB 集成預測前 5 個產品
                       → 發布 forecast_updated 事件

步驟 3: 庫存 + 風險
  ├── 庫存優化代理  → 辨識 32 個低於再訂購點的產品
  │                    → 觸發 reorder_triggered 事件
  └── 風險評估代理  → 評估深度/廣度/關鍵性供應風險

步驟 4: 供應商管理
  └── 供應商管理代理 → 評估供應商、建立 5 筆採購單
                       → HITL 閘門：≥$50K 需人工審批，$10K-$50K 待審核

步驟 5: 物流
  └── 物流協調代理  → 追蹤 5 筆活躍出貨、模擬訂單進度

步驟 6: 戰略規劃
  └── 戰略規劃代理  → 檢視 KPI、執行優化、套用共識機制

步驟 7: 協調仲裁
  └── 協調代理 (CSCO) → 收集 43 個行動、解決衝突、排定優先順序

步驟 8: 報告生成
  └── 報告代理      → 產出 RPT-0001，包含 KPI 快照和代理摘要
```

---

## 研究基礎

本架構整合了最前沿供應鏈 AI 研究的洞見：

| 研究 | 來源 | 應用概念 |
|------|------|---------|
| 京東兩層架構 | ArXiv 2509.03811 | 戰略層 + 戰術層代理分離 |
| 七代理中斷監控 | ArXiv 2601.09680 | 主動監控搭配 7 個專業偵測代理 |
| MARL 庫存補貨 | ArXiv 2511.23366 | 基於 DQN 的強化學習庫存決策 |
| 時序分層多代理系統 | ArXiv 2508.12683 | 三時序層（戰略/戰術/作業） |
| 啤酒遊戲共識機制 | ArXiv 2411.10184 | 跨代理共識以降低牛鞭效應 |

---

## AWS 整合（可選）

ChainCommand 支援可選的 AWS 持久化後端，採用 **Strategy Pattern** 設計。啟用後，週期數據將持久化至 S3/Redshift，並可透過 Athena 和 QuickSight 進行分析——完全不影響預設的記憶體模式。

### 架構

```
PersistenceBackend (ABC)
  ├── NullBackend        # 預設 — 無操作，零開銷
  └── AWSBackend         # S3 + Redshift + Athena + QuickSight
        ├── S3Client         # 上傳 Parquet/JSONL/JSON
        ├── RedshiftClient   # 從 S3 COPY，SQL 查詢
        ├── AthenaClient     # S3 外部表，ad-hoc 查詢
        └── QuickSightClient # 數據集 + 儀表板
```

### 環境變數

```bash
# 啟用 AWS 後端
CC_AWS_ENABLED=true
CC_AWS_REGION=ap-northeast-1

# S3
CC_AWS_S3_BUCKET=chaincommand-data
CC_AWS_S3_PREFIX=supply-chain/

# Redshift
CC_AWS_REDSHIFT_HOST=my-cluster.abc123.redshift.amazonaws.com
CC_AWS_REDSHIFT_PORT=5439
CC_AWS_REDSHIFT_DB=chaincommand
CC_AWS_REDSHIFT_USER=admin
CC_AWS_REDSHIFT_PASSWORD=secret
CC_AWS_REDSHIFT_IAM_ROLE=arn:aws:iam::123456789012:role/RedshiftS3Access

# Athena
CC_AWS_ATHENA_DATABASE=chaincommand
CC_AWS_ATHENA_OUTPUT=s3://chaincommand-data/athena-results/

# QuickSight
CC_AWS_QUICKSIGHT_ACCOUNT_ID=123456789012
```

### 設定步驟

1. **S3 儲存桶** — 在目標區域建立 `chaincommand-data`（或自訂名稱）
2. **Redshift 叢集** — 佈建叢集並建立具有 S3 讀取權限的 IAM 角色以用於 COPY
3. **Athena 工作群組** — 確保預設工作群組（或自訂群組）已配置輸出位置
4. **QuickSight** — （可選）設定 QuickSight 帳戶以建立儀表板
5. **設定環境變數** — 配置上述所有 `CC_AWS_*` 變數
6. **啟動 ChainCommand** — 後端會在首次運行時自動初始化表格和外部表

### AWS API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| `GET` | `/api/aws/status` | AWS 連線狀態與配置 |
| `GET` | `/api/aws/kpi-trend/{metric}?days=30` | 從 Redshift 查詢 KPI 趨勢 |
| `GET` | `/api/aws/query?event_type=low_stock&limit=50` | 透過 Athena 的 ad-hoc 事件查詢 |
| `GET` | `/api/aws/dashboards` | 列出 QuickSight 儀表板 |

### 額外依賴

```bash
pip install boto3 redshift-connector pyarrow
```

---

## 測試

```bash
# 執行所有 AWS 後端測試（47 項測試，無需真實 AWS 憑證）
python -m pytest tests/test_aws/ -v

# 執行特定測試模組
python -m pytest tests/test_aws/test_backend.py -v       # NullBackend, 工廠, AWSBackend
python -m pytest tests/test_aws/test_s3_client.py -v     # S3 上傳/下載操作
python -m pytest tests/test_aws/test_redshift_client.py -v  # Redshift DDL, COPY, 查詢
python -m pytest tests/test_aws/test_athena_client.py -v # Athena 外部表, 輪詢
python -m pytest tests/test_aws/test_quicksight_client.py -v  # QuickSight 數據集, 儀表板
```

| 測試模組 | 測試數 | 覆蓋範圍 |
|---------|--------|---------|
| `test_backend.py` | 17 | NullBackend 無操作、`get_backend()` 工廠、AWSBackend 持久化/查詢 |
| `test_s3_client.py` | 7 | 上傳 Parquet/JSONL/JSON、列出物件、下載、key 格式化 |
| `test_redshift_client.py` | 8 | DDL 建立、COPY 指令、SQL 查詢、KPI 插入、連線 |
| `test_athena_client.py` | 9 | 資料庫/表建立、查詢輪詢、結果解析、逾時 |
| `test_quicksight_client.py` | 6 | 數據來源、數據集、儀表板建立、列出儀表板 |
| **合計** | **47** | 所有 AWS 客戶端皆使用 `unittest.mock` 完全模擬 |

所有測試使用 mocked `boto3` 和 `redshift_connector` — 無需真實 AWS 帳戶或憑證。

---

## 路線圖與未來工作

### 已完成

- [x] **AWS 持久化後端** — S3、Redshift、Athena、QuickSight 整合，透過 Strategy Pattern（`NullBackend` / `AWSBackend`）
- [x] **單元測試套件（AWS）** — 47 項 pytest 測試，使用 mocked boto3/redshift-connector，完整覆蓋所有 AWS 客戶端

### 計畫中的增強功能

- [ ] **真實 LSTM/XGBoost 訓練** — PyTorch LSTM 和 xgboost 整合，達到生產級預測
- [ ] **多階層優化** — 擴展至多倉庫、多層供應鏈網路
- [ ] **串流數據整合** — 透過 Kafka 或 MQTT 連接真實 ERP/WMS 系統
- [ ] **互動式儀表板** — React/Vue 前端搭配即時圖表和代理視覺化
- [ ] **Docker 容器化** — Docker Compose 部署搭配 API 伺服器、工作者和訊息佇列
- [ ] **單元測試套件** — pytest 覆蓋所有模組、代理和 API 端點
- [ ] **代理記憶** — 跨週期持久化代理記憶，支援學習與適應
- [ ] **LangChain/LangGraph 整合** — 結構化工具呼叫和代理圖
- [ ] **Prometheus 指標** — 代理效能和系統健康的可觀測性

### 開放問題

| 問題 | 說明 | 難度 |
|------|------|------|
| 多代理協調 | 優化共識協議以加速收斂 | 困難 |
| 模擬到真實轉移 | 銜接合成數據訓練與真實世界部署 | 困難 |
| 可解釋決策 | 使代理推理對利害關係人透明 | 中等 |
| 對抗魯棒性 | 處理刻意誤導的市場信號 | 困難 |
| 可擴展性 | 支援 1000+ 產品的即時代理協調 | 中等 |

---

## 技術棧

| 層級 | 技術 |
|------|------|
| **程式語言** | Python 3.11+ |
| **數據模型** | Pydantic 2.0+, Pydantic Settings |
| **數據處理** | pandas, numpy |
| **ML/統計** | scikit-learn（Isolation Forest）、自建 LSTM/XGB/GA/DQN |
| **API 伺服器** | FastAPI, uvicorn |
| **非同步執行** | asyncio（Python 原生） |
| **終端 UI** | rich（進度條、表格、樹狀圖） |
| **日誌** | structlog（結構化，ISO 8601） |
| **LLM 客戶端** | openai（可選）、httpx（Ollama，可選） |
| **AWS（可選）** | boto3, redshift-connector, pyarrow（S3, Redshift, Athena, QuickSight） |
| **配置管理** | 環境變數（CC_ 前綴）、.env 檔案 |

### 依賴

```
# 核心（必要）
pydantic>=2.0.0
pydantic-settings>=2.0.0
numpy>=1.21.0
pandas>=1.5.0
structlog>=23.0.0
rich>=13.0.0

# API 伺服器（可選）
fastapi>=0.100.0
uvicorn>=0.20.0

# LLM 後端（可選）
openai>=1.0.0          # 用於 CC_LLM_MODE=openai
httpx>=0.24.0          # 用於 CC_LLM_MODE=ollama

# ML（可選，增強異常偵測）
scikit-learn>=1.0.0    # 用於 Isolation Forest

# AWS 後端（可選，用於 CC_AWS_ENABLED=true）
boto3>=1.28.0          # S3, Athena, QuickSight
redshift-connector>=2.0.0  # Redshift
pyarrow>=12.0.0        # Parquet 支援
```

---

## 貢獻指南

歡迎貢獻！以下是參與方式：

1. **Fork** 此倉庫
2. **建立**功能分支 (`git checkout -b feature/your-feature`)
3. **提交**變更 (`git commit -m 'Add new agent or tool'`)
4. **推送**至分支 (`git push origin feature/your-feature`)
5. **開啟** Pull Request

### 需要協助的領域

- PyTorch LSTM 實作，用於生產級預測
- React/Vue 儀表板前端
- 多週期模擬整合測試
- 額外代理類型（品質檢驗員、財務控制器）
- 真實世界供應鏈數據集適配器
- 文件翻譯

---

## 授權條款

本專案採用 MIT 授權條款 — 詳見 [LICENSE](LICENSE) 檔案。

---

## 致謝

- 架構靈感來自京東自主供應鏈研究和多代理系統文獻
- 啤酒遊戲共識機制改編自 ArXiv 2411.10184
- EOQ 模型基於 Harris-Wilson 公式（1913）
- 統計異常偵測技術來自 scikit-learn 最佳實踐
- 建構於 [ChainInsight](https://github.com/hsinnearth7/supply_chain_insight) — 我們的數據分析前身專案

---

<div align="center">

**由代理驅動，以自主為核心。**

如果這個專案對您有幫助，請考慮給予一顆星！

</div>
