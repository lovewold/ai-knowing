# AI全知 MVP

多源 AI 资讯聚合，按信噪比动态分层，热点看板 + 检索式报告。

## 快速启动

### 1. 配置环境

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

### 2. Docker 启动（推荐，一条命令）

```bash
docker compose up --build
```

API、Worker、Beat、数据库、Redis、前端全部由 Compose 拉起，无需再单独开 PyCharm 多个进程。

访问 **http://localhost:3000**（前端）或 http://localhost:8000（API）

仅改前端 UI 时，可只起后端栈 + 本地 Vite：

```bash
docker compose up -d postgres redis api worker beat
cd frontend && npm install && npm run dev
```

### 3. 手动触发抓取

- 网页：点击顶部「立即抓取」按钮
- API：`POST http://localhost:8000/api/crawl/trigger`

## 前端开发

```bash
cd frontend
npm install
npm run dev
```

开发服务器 http://localhost:3000 ，API 自动代理到 8000 端口。

设计：浅色白底 + 黑色线条，编辑风格排版。

## 配置数据源

编辑 `config/sources.yaml`，添加或修改数据源：

```yaml
sources:
  - id: my-blog
    name: 我的博客
    type: rss
    url: https://example.com/feed
    weight: 25
    language: zh
    enabled: true
```

支持的类型：`rss` | `arxiv` | `hackernews` | `github_trending`

修改后重启 worker：`docker compose restart worker beat`

## 切换 LLM

在 `.env` 中修改：

```
LLM_PROVIDER=deepseek   # deepseek | openai | anthropic
DEEPSEEK_MODEL=deepseek-chat
```

## 项目结构

```
config/          # 数据源与信噪比配置
backend/         # FastAPI 后端 + Celery
frontend/        # React 前端 (Vite + Tailwind)
  src/
    pages/       # 首页 / 报告 / 资讯 / 数据源
    components/  # UI 组件
```

## API

| 端点 | 说明 |
|------|------|
| `GET /` | 首页（报告 + 资讯列表） |
| `GET /reports/{id}` | 报告详情 |
| `GET /api/reports` | 报告 JSON 列表 |
| `GET /api/articles` | 资讯 JSON 列表 |
| `GET /api/sources` | 当前数据源配置 |
| `POST /api/crawl/trigger` | 触发抓取流水线 |

## 本地开发（无 Docker）

```bash
cd backend
pip install -r requirements.txt
set CONFIG_DIR=../config
set DATABASE_URL=postgresql://aiknow:aiknow@localhost:5432/aiknow
set REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --reload
```

## 运行测试

```bash
cd backend
set CONFIG_DIR=../config
pytest tests/ -v
```
