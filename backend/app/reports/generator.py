from app.config import settings
from app.llm.resolver import get_llm_provider
from app.models import AgentTool, RawArticle, Report, ReportType

SYSTEM_PROMPT = """你是 AI全知 平台的技术分析师。基于提供的原始资讯，生成结构化、客观、可验证的技术报告。
要求：
1. 使用 Markdown 格式
2. 区分事实与推断，推断需标注「推测」
3. 引用原始来源
4. 语言：{language}
5. 标注信息时效性限制
"""

TREND_TEMPLATE = """请基于以下资讯生成【AI 行业趋势/新闻分析报告】（全部中文）：

标题：{title}
来源：{source}
链接：{url}
摘要：{summary}
信号强度：{score}

报告结构：
## 事件摘要
## 技术影响分析
## 关联技术栈
## 行业趋势判断
## 可信度评估
## 关注建议
"""

TOOL_TEMPLATE = """请基于以下资讯生成【工具/模型评测报告】（全部中文）：

标题：{title}
来源：{source}
链接：{url}
摘要：{summary}
信号强度：{score}

报告结构：
## 核心能力概述
## 与现有方案对比
## 上手门槛与部署难度
## 维护健康度
## 适用场景
## 不适用场景
## 该不该关注（结论）
"""

AGENT_TOOL_TEMPLATE = """请基于以下 Agent 工具/框架信息，生成【Agent 工具调研报告】（全部中文）：

名称：{title}
来源：{source}
链接：{url}
简介：{summary}
信号强度：{score}

报告结构：
## 工具概述
## 核心能力与架构
## 与其他 Agent 框架对比
## 适用场景
## 上手难度与部署方式
## 社区活跃度与维护状态
## 推荐指数与结论
"""

SCENARIO_TEMPLATE = """请基于以下技术资讯，生成【应用场景衍生报告】（全部中文）：

标题：{title}
来源：{source}
链接：{url}
摘要：{summary}

报告结构：
## 技术能力提炼
## 场景应用分析（至少3个场景）
## 综合落地建议
## 风险与限制
"""

AGENT_SURVEY_TEMPLATE = """请基于以下 Agent 工具清单，生成【AI Agent 工具全景调研报告】（全部中文）。

当前收录 {tool_count} 个 Agent 相关工具/框架：

{tool_list}

报告结构：
## 执行摘要
## Agent 生态全景图（框架/平台/SDK/协议/工作流）
## 主流方案深度对比
## 2026 年 Agent 技术趋势
## 选型决策树
## 新兴工具值得关注
## 风险与避坑指南
## 总结与行动建议
"""

CUSTOM_SYSTEM = """你是 AI全知 平台的高级报告分析师。用户会用自然语言描述他们想要的报告类型、分析角度和内容重点。
要求：
1. 深入理解用户意图，生成符合描述的 Markdown 报告（可灵活组织结构，不必拘泥于固定模板）
2. 充分利用提供的背景资料（资讯、Agent 工具、已有报告）
3. 区分事实与推断，推断需标注「推测」
4. 引用原始来源链接
5. 语言：{language}
6. 报告必须以一级标题 (# ...) 开头，标题简洁概括主题
7. 标注信息时效性限制
"""


def _extract_title(content: str, fallback: str) -> tuple[str, str]:
    lines = content.strip().split("\n")
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:]).lstrip()
        return title[:500], body if body else content
    return fallback[:500], content


def _format_articles_context(articles: list[RawArticle]) -> str:
    if not articles:
        return "（无相关资讯）"
    blocks = []
    for i, a in enumerate(articles, 1):
        score = a.signal.score if a.signal else None
        score_str = f"{score:.2f}" if score is not None else "N/A"
        blocks.append(
            f"{i}. **{a.title_zh or a.title}**\n"
            f"   - 来源: {a.source_name} | 信号: {score_str} | 分类: {a.category}\n"
            f"   - 链接: {a.url}\n"
            f"   - 摘要: {a.summary_zh or a.summary or '（无）'}"
        )
    return "\n".join(blocks)


def _format_tools_context(tools: list[AgentTool]) -> str:
    if not tools:
        return "（无 Agent 工具数据）"
    lines = []
    for i, t in enumerate(tools, 1):
        name = t.name_zh or t.name
        desc = t.description_zh or t.description or "暂无描述"
        stars = f" | Stars: {t.stars}" if t.stars else ""
        typ = f" | 类型: {t.tool_type}" if t.tool_type else ""
        lines.append(f"{i}. **{name}**{typ}{stars}\n   - 链接: {t.url}\n   - 简介: {desc}")
    return "\n".join(lines)


def _format_reports_context(reports: list[Report]) -> str:
    if not reports:
        return "（无已有报告）"
    blocks = []
    for i, r in enumerate(reports, 1):
        preview = r.content_md[:800] + ("..." if len(r.content_md) > 800 else "")
        blocks.append(f"{i}. **{r.title}** ({r.report_type.value})\n{preview}")
    return "\n\n".join(blocks)


async def generate_custom_report(
    user_prompt: str,
    *,
    articles: list[RawArticle] | None = None,
    tools: list[AgentTool] | None = None,
    existing_reports: list[Report] | None = None,
) -> Report:
    llm = get_llm_provider(task="custom")
    lang = "中文" if settings.report_language == "zh" else "English"
    system = CUSTOM_SYSTEM.format(language=lang)

    context_parts = [f"## 用户需求\n\n{user_prompt.strip()}"]
    if articles:
        context_parts.append(f"## 相关资讯（{len(articles)} 条）\n\n{_format_articles_context(articles)}")
    if tools:
        context_parts.append(f"## Agent 工具库（{len(tools)} 个）\n\n{_format_tools_context(tools)}")
    if existing_reports:
        context_parts.append(f"## 已有报告参考（{len(existing_reports)} 份）\n\n{_format_reports_context(existing_reports)}")

    context_parts.append(
        "\n请根据用户需求撰写完整报告。若用户未指定结构，请自行设计最合适的章节。"
        "报告必须以 `# 报告标题` 作为第一行。"
    )
    full_prompt = "\n\n".join(context_parts)
    content = await llm.generate(system, full_prompt)

    fallback_title = user_prompt.strip()[:80] + ("..." if len(user_prompt.strip()) > 80 else "")
    title, body = _extract_title(content, fallback_title)
    if body != content:
        content = f"# {title}\n\n{body}"

    article_id = articles[0].id if articles and len(articles) == 1 else None
    return Report(
        article_id=article_id,
        report_type=ReportType.CUSTOM,
        title=f"[自定义] {title}"[:500],
        content_md=content,
        user_prompt=user_prompt.strip(),
        quality_label="AI定制",
    )


def _article_context(article: RawArticle, score: float) -> dict:
    return {
        "title": article.title_zh or article.title,
        "source": article.source_name,
        "url": article.url,
        "summary": article.summary_zh or article.summary or "（无摘要）",
        "score": f"{score:.2f}",
    }


async def generate_report(article: RawArticle, report_type: str, score: float) -> Report:
    llm = get_llm_provider(task="report")
    lang = "中文" if settings.report_language == "zh" else "English"
    system = SYSTEM_PROMPT.format(language=lang)
    context = _article_context(article, score)

    if report_type == "agent":
        user_prompt = AGENT_TOOL_TEMPLATE.format(**context)
        rtype = ReportType.TOOL
        prefix = "[Agent调研]"
    elif report_type == "tool":
        user_prompt = TOOL_TEMPLATE.format(**context)
        rtype = ReportType.TOOL
        prefix = "[工具评测]"
    elif report_type == "scenario":
        user_prompt = SCENARIO_TEMPLATE.format(**context)
        rtype = ReportType.SCENARIO
        prefix = "[场景衍生]"
    else:
        user_prompt = TREND_TEMPLATE.format(**context)
        rtype = ReportType.TREND
        prefix = "[趋势分析]"

    content = await llm.generate(system, user_prompt)
    display_title = article.title_zh or article.title
    return Report(
        article_id=article.id,
        report_type=rtype,
        title=f"{prefix} {display_title}"[:500],
        content_md=content,
        quality_label="AI初稿",
    )


async def generate_scenario_report(article: RawArticle, primary_report: Report) -> Report:
    llm = get_llm_provider(task="report")
    lang = "中文" if settings.report_language == "zh" else "English"
    system = SYSTEM_PROMPT.format(language=lang)
    title = article.title_zh or article.title

    user_prompt = f"""基于以下已生成的技术报告，进一步生成【应用场景衍生报告】（全部中文）：

原始标题：{title}
原始链接：{article.url}

已有报告：
{primary_report.content_md}

请分析：若企业/开发者采用该最新技术，在软件开发、内容创作、知识工作、客户服务等场景能做什么、预期效果如何、落地难度如何。
"""
    content = await llm.generate(system, user_prompt)
    return Report(
        article_id=article.id,
        report_type=ReportType.SCENARIO,
        title=f"[场景衍生] {title}"[:500],
        content_md=content,
        quality_label="AI初稿",
    )


async def generate_agent_survey_report(tools: list[AgentTool]) -> Report:
    llm = get_llm_provider(task="agent")
    lang = "中文" if settings.report_language == "zh" else "English"
    system = SYSTEM_PROMPT.format(language=lang)

    lines = []
    for i, t in enumerate(tools, 1):
        name = t.name_zh or t.name
        desc = t.description_zh or t.description or "暂无描述"
        stars = f" | Stars: {t.stars}" if t.stars else ""
        typ = f" | 类型: {t.tool_type}" if t.tool_type else ""
        lines.append(f"{i}. **{name}**{typ}{stars}\n   - 链接: {t.url}\n   - 简介: {desc}")

    tool_list = "\n".join(lines) if lines else "（暂无工具数据）"
    user_prompt = AGENT_SURVEY_TEMPLATE.format(tool_count=len(tools), tool_list=tool_list)
    content = await llm.generate(system, user_prompt)

    return Report(
        article_id=None,
        report_type=ReportType.AGENT_SURVEY,
        title="[Agent全景] AI Agent 工具全景调研报告",
        content_md=content,
        quality_label="AI初稿",
    )
