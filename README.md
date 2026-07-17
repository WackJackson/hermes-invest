# Hermes Invest Core

个人投资助手第一版工程骨架，定位是面向长期持有、价值投资策略的持仓驱动型投资助手。

## 项目目标

- 以真实持仓为中心，而不是纯聊天机器人
- 支持 A 股、港股、美股持仓分析
- Hermes 负责飞书入口、消息编排和会话管理
- Investment Core 负责持仓、成本、仓位、规则、分析和报告
- 独立部署，不影响服务器现有 `pitchasso` 项目

## 当前范围

当前仓库先落地 MVP 的 Investment Core 服务骨架：

- 持仓导入：CSV / Excel
- 组合概览：收益、仓位、市场分布
- 日报分析：基于结构化规则生成建议
- Hermes 上下文接口：给编排层输出结构化 payload
- SQLite 持久化
- Docker Compose 独立部署

## 架构原则

- Hermes 只做入口和编排，不承载核心投资逻辑
- 投资核心必须独立、可测试、可迁移
- 第一版优先轻量，避免 Redis、向量库、本地模型、多 worker
- 对服务器现有端口零侵入，不碰 `8000`、`80`、`443`

## 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
uvicorn investment_core.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

## 核心接口

### 1. 健康检查

```bash
curl http://127.0.0.1:8000/healthz
```

### 2. 导入持仓

```bash
curl -X POST http://127.0.0.1:8000/api/v1/holdings/import \
  -F 'file=@sample_data/holdings.example.csv'
```

### 3. 组合概览

```bash
curl -X POST http://127.0.0.1:8000/api/v1/portfolio/overview \
  -H 'Content-Type: application/json' \
  -d '{
    "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
    "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2}
  }'
```

### 4. 更新投资规则画像

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/rules/profile \
  -H 'Content-Type: application/json' \
  -d '{
    "focus_metrics": ["roe", "free_cash_flow"],
    "forbidden_traits": ["high-debt", "serial-dilution"],
    "target_holding_years": 5,
    "max_single_position_pct": 35,
    "max_drawdown_review_pct": 12,
    "alert_return_pct": 25,
    "daily_sections": ["overview", "risk", "news"],
    "weekly_sections": ["allocation", "valuation", "watchlist"]
  }'
```

### 5. 日报分析

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analysis/daily \
  -H 'Content-Type: application/json' \
  -d '{
    "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
    "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2}
  }'
```

### 6. Hermes 编排上下文

```bash
curl -X POST http://127.0.0.1:8000/api/v1/hermes/context \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "今天组合里最需要关注什么？",
    "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
    "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2}
  }'
```

## 生产部署

目标部署目录建议：`/opt/hermes-invest`

### 1. 复制项目到服务器

```bash
rsync -av ./ user@8.160.165.34:/opt/hermes-invest/
```

### 2. 可选但强烈建议：先加 1G swap

这台机器内存太抠了，不加 swap 后面很容易 OOM，真不是吓唬你。

```bash
cd /opt/hermes-invest
bash scripts/server/add_swap.sh
```

### 3. 启动容器

```bash
cd /opt/hermes-invest
cp .env.example .env
bash scripts/server/deploy.sh
```

### 4. 验证服务

```bash
curl http://127.0.0.1:18080/healthz
```

## Docker 设计

- 容器名：`hermes-invest-core`
- 映射端口：`127.0.0.1:18080 -> 8080`
- 数据目录：`./data`
- 数据库：SQLite
- 内存限制：`512m`
- CPU 限制：`0.75`

## 下一阶段待接入

- Hermes 真正的飞书入口与消息编排
- 市场数据源接入：AkShare / yfinance / Finnhub 等
- 定时任务：日报 / 周报 / 异动提醒
- LLM API 适配层
- 真实投资规则建模
- 持仓快照和分析历史

## 文档

- `docs/architecture.md`：系统架构
- `docs/deployment.md`：部署与 Nginx 接入
- `sample_data/holdings.example.csv`：样例持仓
