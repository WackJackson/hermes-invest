from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from investment_core.config import get_db_path, get_root_path
from investment_core.routes import analysis_router, hermes_router, holdings_router, rules_router
from investment_core.storage import Storage


def create_app(db_path: str | Path | None = None, root_path: str = "") -> FastAPI:
    app = FastAPI(
        title="Hermes Investment Core",
        version="0.1.0",
        description="Lightweight investment core service for personal long-term value investing workflows",
        root_path=root_path,
    )
    app.state.storage = Storage(Path(db_path) if db_path else get_db_path())

    @app.get("/", tags=["home"], response_class=HTMLResponse)
    def home(request: Request) -> str:
        prefix = request.scope.get("root_path", "") or ""
        docs_url = f"{prefix}/docs" if prefix else "/docs"
        openapi_url = f"{prefix}/openapi.json" if prefix else "/openapi.json"
        return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Hermes Investment Core</title>
  <style>
    :root {{
      --bg: #f4f1e8;
      --ink: #1d2a23;
      --accent: #a9502d;
      --panel: #fffdf8;
      --line: #d7cdbd;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Georgia, "Times New Roman", serif; background: radial-gradient(circle at top, #fffdf6, var(--bg)); color: var(--ink); }}
    main {{ max-width: 920px; margin: 0 auto; padding: 56px 24px 72px; }}
    h1 {{ font-size: clamp(40px, 7vw, 76px); line-height: 0.95; margin: 0 0 16px; font-weight: 700; letter-spacing: -0.04em; }}
    p {{ font-size: 18px; line-height: 1.6; max-width: 720px; }}
    .panel {{ margin-top: 32px; padding: 28px; background: var(--panel); border: 1px solid var(--line); border-radius: 18px; box-shadow: 0 14px 40px rgba(29, 42, 35, 0.08); }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 14px; margin-top: 24px; }}
    a {{ color: inherit; text-decoration: none; }}
    .button {{ padding: 14px 18px; border-radius: 999px; border: 1px solid var(--ink); font-size: 15px; }}
    .primary {{ background: var(--ink); color: #f9f5ec; border-color: var(--ink); }}
    code {{ font-family: "SFMono-Regular", Menlo, monospace; font-size: 14px; background: #efe7da; padding: 2px 6px; border-radius: 6px; }}
    ul {{ padding-left: 20px; line-height: 1.7; }}
  </style>
</head>
<body>
  <main>
    <h1>Hermes Investment Core</h1>
    <p>个人投资助手核心服务已运行。当前版本提供持仓导入、组合概览、规则画像、日报分析和 Hermes 编排上下文接口。</p>
    <div class="panel">
      <strong>当前访问方式</strong>
      <p>这个服务适合挂在反向代理路径下，例如 <code>/invest/</code>。文档和 OpenAPI 已支持前缀部署。</p>
      <div class="actions">
        <a class="button primary" href="{docs_url}">打开 API 文档</a>
        <a class="button" href="{openapi_url}">查看 OpenAPI</a>
      </div>
      <ul>
        <li>健康检查：<code>{prefix}/healthz</code></li>
        <li>持仓导入：<code>{prefix}/api/v1/holdings/import</code></li>
        <li>Hermes 上下文：<code>{prefix}/api/v1/hermes/context</code></li>
      </ul>
    </div>
  </main>
</body>
</html>
"""

    @app.get("/healthz", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(holdings_router)
    app.include_router(rules_router)
    app.include_router(analysis_router)
    app.include_router(hermes_router)
    return app


app = create_app(root_path=get_root_path())
