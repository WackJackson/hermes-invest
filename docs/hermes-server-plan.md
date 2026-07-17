# Hermes 服务器部署计划

## 目标

在不影响现有 `pitchasso` 与 `hermes-invest-core` 的前提下，新增独立 Hermes 运行环境，先打通：

- Hermes CLI / gateway
- Feishu 平台
- MCP 调 `invest_core`

## 运行原则

- Hermes 独立目录：`/opt/hermes-agent`
- 不进现有 `pitchasso` 容器
- 不和 `hermes-invest-core` 共容器
- 第一阶段优先 CLI + Feishu gateway，不启 dashboard

## 为什么先不启 dashboard

Hermes 自带 dashboard，但对这台 2G 机器没必要先开。

当前机器已经跑：

- nginx
- mysql
- docker
- pitchasso
- hermes-invest-core

再把 Hermes dashboard 一起打开，纯属给自己找麻烦。

## 第一阶段推荐安装方式

不要一开始就把 Hermes 整个 Docker Compose 套餐搬上去。

推荐：

1. 服务器安装 `uv`
2. 建立独立目录 `/opt/hermes-agent`
3. 用 `uv venv` 建 Python 3.11 环境
4. `uv pip install -e '.[mcp,feishu]'`
5. 写 `~/.hermes/config.yaml`
6. 用 systemd 跑 `hermes gateway run`

这样比它默认整套容器更轻。

## Feishu 所需变量

至少：

```bash
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_CONNECTION_MODE=websocket
```

可选：

```bash
FEISHU_ALLOWED_USERS=
FEISHU_HOME_CHANNEL=
FEISHU_ENCRYPT_KEY=
FEISHU_VERIFICATION_TOKEN=
```

## MCP 配置

Hermes 通过 `~/.hermes/config.yaml` 接入：

```yaml
mcp_servers:
  invest_core:
    command: "python3"
    args:
      - "/opt/hermes-invest/src/investment_core/mcp_server.py"
    env:
      INVEST_DB_PATH: "/opt/hermes-invest/data/investment_core.db"
```

## 最小验证链路

先不要直接上飞书对话，顺序必须是：

1. 服务器启动 Hermes CLI
2. 在 CLI 中验证 MCP 工具被发现
3. 能调用 `portfolio_overview` / `hermes_context`
4. 再启 `hermes gateway run`
5. 再用飞书发消息测试

## 当前阻塞

正式部署 Hermes 前还需要确认：

1. 服务器上是否已有 Python 3.11 / uv / Node
2. Feishu 机器人是否需要限制 `FEISHU_ALLOWED_USERS`
3. 你准备用哪个 LLM provider 跑 Hermes

## 我下一步会做什么

1. SSH 上服务器检查 Python / uv / Node
2. 建 `/opt/hermes-agent`
3. 选最省资源的安装路径
4. 先把 Hermes CLI + MCP 跑起来
