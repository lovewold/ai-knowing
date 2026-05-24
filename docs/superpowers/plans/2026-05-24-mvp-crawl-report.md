# AI全知 MVP 抓取+报告 实现计划

> **Goal:** 跑通抓取 → 信噪比过滤 → DeepSeek 报告生成流水线

**Architecture:** FastAPI + Celery + PostgreSQL + Redis，YAML 配置数据源，Docker Compose 部署

**Tech Stack:** Python 3.11, FastAPI, Celery, feedparser, httpx, DeepSeek API

---

## 任务清单

- [x] 项目骨架与 Docker Compose
- [x] 可配置数据源 (sources.yaml)
- [x] 爬虫引擎 (RSS/ArXiv/HN/GitHub)
- [x] 信噪比计算
- [x] LLM Provider 抽象 + DeepSeek
- [x] 三类报告生成
- [x] Celery 定时任务
- [x] FastAPI 展示层
- [x] 单元测试
