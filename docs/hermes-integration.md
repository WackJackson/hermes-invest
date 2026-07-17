# Hermes 接入方案

## 结论

Hermes 现在就能接，不需要再推翻现有 Investment Core。

最稳的接法不是把投资逻辑塞进 Hermes 的 prompt，也不是先大改 Hermes 源码，而是：

- Hermes 负责飞书入口、会话管理、工具编排、定时投递
- Investment Core 继续独立运行在 `127.0.0.1:18080`
- 用 MCP 把 Investment Core 暴露成 Hermes 可调用工具

这条路最符合你前面定的原则，而且对 2G 机器最友好。

## 为什么选 MCP 接法

Hermes 原生支持 MCP 客户端。

根据上游仓库文档：

- Hermes 启动时会读取 `~/.hermes/config.yaml` 的 `mcp_servers`
- 自动发现 MCP 工具
- 自动注入所有平台工具集
- Feishu 是 Hermes 原生支持的平台之一

这意味着我们不需要先魔改 Hermes 内核，只需要提供一个轻量 MCP Server，把下面这些能力作为工具暴露出去：

- 导入持仓
- 获取组合概览
- 更新投资规则
- 生成日报分析
- 生成 Hermes 上下文

## 推荐架构

```text
Feishu
  |
  v
Hermes Gateway
  |
  +--> LLM Provider
  |
  +--> MCP: invest-core-mcp
            |
            v
      Investment Core API
      http://127.0.0.1:18080
```

## 第一阶段目标

第一阶段只做最小闭环：

1. Hermes 在服务器独立运行
2. Hermes 打开 Feishu 平台
3. Hermes 通过 MCP 调用 Investment Core
4. 飞书中可以问：
   - 当前组合概览
   - 今日组合分析
   - 重点关注哪些持仓

## 不建议的错误路线

### 路线 1：把投资逻辑写进 Hermes prompt

这会把组合事实、规则阈值、持仓结构全部混进自然语言上下文里，后面一定烂。

### 路线 2：直接改 Hermes 大量源码

这会增加升级成本，也会把后续维护变成一坨屎。

### 路线 3：先上重型消息/调度/缓存组件

2G 机器根本不值得这么玩。

## 具体落地步骤

### Step 1. 新增 MCP Server

在当前仓库新增一个轻量 `invest_core_mcp` 服务，负责把 HTTP API 映射成 MCP tools。

建议暴露这些工具：

- `portfolio_overview`
- `daily_analysis`
- `update_rule_profile`
- `list_holdings`
- `import_holdings_csv`
- `hermes_context`

MCP Server 本身只做转发和参数校验，不承载业务逻辑。

### Step 2. 准备 Hermes 独立目录

服务器建议目录：

- `/opt/hermes-agent`
- `/opt/hermes-invest` 继续保留给 Investment Core

Hermes 不应和 Investment Core 共容器。

### Step 3. 配置 Hermes MCP

Hermes 文档建议在 `~/.hermes/config.yaml` 写 `mcp_servers`。

最终会像这样：

```yaml
mcp_servers:
  invest_core:
    command: "python3"
    args:
      - "/opt/hermes-invest/mcp_server.py"
    env:
      INVEST_CORE_BASE_URL: "http://127.0.0.1:18080"
```

### Step 4. 打开 Feishu 平台

Hermes 原生支持 Feishu，最小需要：

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

如果你走回调模式，还要：

- `FEISHU_ENCRYPT_KEY`
- `FEISHU_VERIFICATION_TOKEN`

Hermes 上游代码里默认支持：

- `FEISHU_CONNECTION_MODE=websocket`
- 或回调模式配置

第一阶段建议先看你飞书应用怎么配，再决定 websocket 还是 webhook。

### Step 5. 定义 Hermes 系统指令

Hermes 需要一个非常明确的系统约束：

- 所有投资结论优先调用 `invest_core` 工具
- 不能凭空捏造持仓、成本、收益、仓位
- LLM 只负责解释、总结、提炼

## 当前阻塞项

现在还没正式接 Hermes，主要缺这几样：

1. 你的 Feishu 应用配置
2. 你要用的 LLM 提供商与 Key
3. MCP Server 这层还没在当前仓库实现
4. Hermes 服务器独立部署目录还没落地

## 下一步建议

最合理的执行顺序：

1. 先在当前仓库实现 `invest_core_mcp`
2. 本地验证 MCP -> HTTP 转发可用
3. 再部署 Hermes 到服务器
4. 最后接 Feishu

别反过来。先上 Feishu 再补工具层，只会让链路排查变成灾难。
