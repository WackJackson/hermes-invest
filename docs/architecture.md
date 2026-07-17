# 架构说明

## 1. 总体架构

```text
Feishu / Scheduler / Future Channels
              |
              v
           Hermes
    (会话、编排、工具调用)
              |
              v
      Investment Core API
  (持仓、成本、仓位、规则、分析)
              |
              v
           SQLite
```

## 2. 组件职责

### Hermes

职责：

- 飞书消息入口
- 用户会话管理
- 调用 Investment Core
- 调用外部 LLM 生成自然语言回复
- 定时触发日报、周报、异动消息

不负责：

- 持仓主数据
- 成本和收益计算
- 投资规则决策
- 组合分析逻辑

### Investment Core

职责：

- 持仓导入与读取
- 组合概览计算
- 多市场和多币种统一估值
- 投资规则画像存储
- 结构化日报分析
- 向 Hermes 输出结构化上下文

### SQLite

第一版只存这些关键数据：

- 持仓明细
- 投资规则画像
- 后续可扩展分析历史和推送记录

## 3. 为什么这样拆

原因很直接：

- Hermes 擅长入口、会话和工具编排
- 投资逻辑需要可测试、可追溯、可替换
- 如果把持仓和规则都塞进 prompt，后面一定烂成一锅粥
- 2C2G 小机器扛不住重型中间件和乱七八糟的自治 Agent

## 4. 第一版接口边界

### `/api/v1/holdings/import`

输入 CSV 或 Excel，替换当前持仓。

### `/api/v1/portfolio/overview`

输入最新价格和汇率，返回组合概览。

### `/api/v1/rules/profile`

读取或更新用户的价值投资规则画像。

### `/api/v1/analysis/daily`

输出日报结构化分析，包括建议和报告提纲。

### `/api/v1/hermes/context`

输出给 Hermes 的消息编排上下文，避免 LLM 胡编组合事实。

## 5. 后续扩展建议

### 数据源层

后续单独拆一层 `market_data`：

- A 股：AkShare / Tushare
- 港美股：yfinance / Finnhub
- 新闻：聚合接口或专门新闻源

### 调度层

别一上来就塞 Celery，第一版完全没必要。

可选路线：

- 先用 Hermes 自带调度能力
- 或者单独用 cron 调 HTTP 接口

### 分析规则层

现在只做静态规则阈值，后续再往下扩：

- 估值区间
- 行业集中度
- 币种暴露
- 回撤分层策略
- 重大新闻和财报事件触发
