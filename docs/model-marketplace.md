# 模型广场与知识库产品清单

## 模型广场

- **数据源**：[AGICTO 模型广场](https://agicto.com/model)
- **前台路径**：`/models`、`/models/{slug}`
- **同步 API**：`POST /api/marketplace/sync?fetch_docs=true&doc_limit=40`

### 同步流程

1. 抓取列表页 RSC 内嵌 JSON（约 290+ 模型）：名称、厂商、场景、价格、上下文长度
2. 可选批量抓取详情页完整 Markdown 文档（`mdContent` 字段）
3. 写入 `model_catalog_entries` 表

### 筛选维度

| 参数 | 说明 |
|------|------|
| `provider` | 提供公司（OpenAI、DeepSeek、阿里…） |
| `scene` | 使用场景（文本、图像、向量、音频…） |
| `free` | 是否免费 |
| `q` | 搜索模型名 |

---

## 知识库产品清单

配置文件：`config/product_catalog.yaml`

### 当前分类（共 40+ 条目）

| 分类 | 示例 |
|------|------|
| IDE | Cursor、Windsurf、Copilot、Continue、Aider |
| Agent平台 | Coze、Dify、FastGPT、LangFlow、n8n |
| 对话助手 | ChatGPT、Claude、Gemini、Kimi、豆包 |
| 图像视频 | Midjourney、Runway、可灵 |
| RAG框架 | LangChain、LlamaIndex、Haystack |
| 向量数据库 | Pinecone、Milvus、Qdrant、Chroma |
| 模型托管 | Ollama、vLLM、LM Studio |
| 大模型API | DeepSeek、GPT-4o、Claude、通义、智谱 |

查看完整清单：`GET /api/knowledge/catalog`

---

## 自动补齐文档

对知识库条目中 **缺少 content_md** 的条目：

1. 优先使用 YAML 中的 `readme_url`
2. 若 `external_url` 为 GitHub/GitLab，自动尝试 `README.md` raw 地址
3. 写入后自动 reindex 向量

触发：`POST /api/knowledge/enrich?limit=30`（管理后台「补齐官网 README」）

---

## 后续规划

- [ ] 按「类型 × 产品」二级分类 UI
- [ ] 模型广场与知识库模型条目关联
- [ ] 定时 Celery 任务增量同步 AGICTO
