# AI全知 MVP：抓取 + 自动报告 设计文档

> **版本**：v1.0 | **日期**：2026-05-24 | **状态**：已批准

## 目标

构建以知识库为核心的 AI 行业资讯自动抓取与报告生成流水线，优先跑通内容生产，Web 展示从简。

## 已确认决策

| 项 | 决策 |
|---|---|
| 优先级 | 抓取 + 自动报告（界面从简） |
| LLM | 多 Provider 可切换，默认 DeepSeek |
| 部署 | 本地 Windows 开发 → Docker 上云 |
| 数据源 | 中英混合 + YAML 可配置 |

## 架构

```
sources.yaml → 爬虫引擎 → 去重 → 信噪比计算 → 报告队列 → LLM 生成 → PostgreSQL → FastAPI 展示
```

## 核心模块

1. **可配置数据源** — `config/sources.yaml`，支持 rss/github_trending/hackernews/arxiv
2. **信噪比计算** — 纯代码公式，阈值 0.70/0.45
3. **报告工厂** — 趋势报告、工具评测、应用场景衍生
4. **LLM 抽象层** — DeepSeek/OpenAI/Claude 可切换
5. **任务调度** — Celery Beat 每 2 小时抓取

## MVP 边界

**包含**：5-8 内置源、YAML 配置、三类报告、REST API、极简 Web、Docker Compose

**不包含**：三 AI 对抗审查、知识图谱、用户系统、社区、公众号抓取
