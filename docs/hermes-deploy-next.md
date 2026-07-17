# Hermes 下一步部署

## 当前已完成

- Investment Core 已部署到服务器
- `https://pitchasso.cn/invest/` 已加 Basic Auth
- 当前仓库已增加 MCP Server：`src/investment_core/mcp_server.py`

## 推荐的 Hermes 接入方式

不要把投资逻辑写进 Hermes 本体。

建议：

1. 服务器单独部署 Hermes 到 `/opt/hermes-agent`
2. Hermes 通过 MCP 调 `invest-core`
3. Hermes 开 Feishu 平台

## MCP 配置示例

Hermes 的 `~/.hermes/config.yaml` 里增加：

```yaml
mcp_servers:
  invest_core:
    command: "python3"
    args:
      - "/opt/hermes-invest/src/investment_core/mcp_server.py"
    env:
      INVEST_DB_PATH: "/opt/hermes-invest/data/investment_core.db"
```

## Feishu 环境变量

最少需要：

```bash
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_CONNECTION_MODE=websocket
```

如果后面走公网回调，再加：

```bash
FEISHU_ENCRYPT_KEY=...
FEISHU_VERIFICATION_TOKEN=...
```

## 推荐执行顺序

1. 把 Hermes 安装在服务器
2. 写好 `~/.hermes/config.yaml`
3. 让 Hermes 先在 CLI 模式下跑通 MCP
4. 再启 Feishu gateway

## 风险提醒

Hermes 本体比当前 Investment Core 重，2G 机器上必须克制：

- 不开多余平台
- 不装无关插件
- 先只开 Feishu
- 先只开最少模型和工具
