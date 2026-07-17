# 部署说明

## 1. 部署原则

这套项目部署必须满足下面这些死规矩：

- 不影响现有 `pitchasso`
- 不复用其容器
- 不占用 `8000`
- 不直接监听公网端口
- 外部访问统一走现有 Nginx 反代

## 2. 目录规划

建议目录：`/opt/hermes-invest`

建议内容：

- 代码：`/opt/hermes-invest`
- 数据：`/opt/hermes-invest/data`
- 环境变量：`/opt/hermes-invest/.env`

## 3. Compose 端口设计

容器暴露：`8080`

宿主机绑定：`127.0.0.1:18080`

这意味着：

- 外网打不到这个服务
- 只有本机 Nginx 可以通过 `127.0.0.1:18080` 转发
- 不会跟 `pitchasso` 的 `8000` 冲突

## 4. 建议的 Nginx 反代

你现在还没把 `pitchasso` 现有配置贴出来，所以这里先给一个独立站点样板，别他妈直接无脑覆盖线上配置。

```nginx
server {
    listen 80;
    server_name invest.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

如果后面要接飞书事件回调，可以把回调路径单独挂在一个 location 上。

## 5. 部署步骤

### 5.1 上传代码

```bash
rsync -av ./ user@8.160.165.34:/opt/hermes-invest/
```

### 5.2 加 swap

这一步很值得做，不然 2G 不到的可用内存真他妈脆。

```bash
ssh user@8.160.165.34
cd /opt/hermes-invest
bash scripts/server/add_swap.sh
```

### 5.3 启动服务

```bash
cd /opt/hermes-invest
cp .env.example .env
docker compose build
docker compose up -d
```

### 5.4 检查运行状态

```bash
docker compose ps
docker logs hermes-invest-core --tail 100
curl http://127.0.0.1:18080/healthz
```

## 6. 风险点

### 内存

当前机器最危险的是内存，不是 CPU。

避免做这些脑残操作：

- 不要上 Redis
- 不要上本地大模型
- 不要开多 worker
- 不要再加一堆监控组件

### 数据源

市场数据接口以后要做熔断和降级，不然外部 API 一抽风，日报就会跟着炸。

### SQLite

第一版够用，但后面如果要存历史快照、新闻和推送记录，可能要迁到 MySQL。真到那一步，也必须使用新表前缀，不能乱碰共享实例里的别的项目表。
