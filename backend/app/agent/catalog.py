import re

from sqlalchemy.orm import Session

from app.localization import is_agent_related
from app.models import AgentTool, RawArticle

KNOWN_AGENT_TOOLS = [
    {"name": "LangChain", "url": "https://github.com/langchain-ai/langchain", "tool_type": "框架"},
    {"name": "LangGraph", "url": "https://github.com/langchain-ai/langgraph", "tool_type": "框架"},
    {"name": "CrewAI", "url": "https://github.com/crewAIInc/crewAI", "tool_type": "多Agent"},
    {"name": "AutoGen", "url": "https://github.com/microsoft/autogen", "tool_type": "多Agent"},
    {"name": "LlamaIndex", "url": "https://github.com/run-llama/llama_index", "tool_type": "RAG/Agent"},
    {"name": "Dify", "url": "https://github.com/langgenius/dify", "tool_type": "平台"},
    {"name": "Coze", "url": "https://www.coze.com", "tool_type": "平台"},
    {"name": "OpenAI Agents SDK", "url": "https://github.com/openai/openai-agents-python", "tool_type": "SDK"},
    {"name": "MCP", "url": "https://github.com/modelcontextprotocol", "tool_type": "协议"},
    {"name": "n8n", "url": "https://github.com/n8n-io/n8n", "tool_type": "工作流"},
    {"name": "Flowise", "url": "https://github.com/FlowiseAI/Flowise", "tool_type": "低代码"},
    {"name": "Semantic Kernel", "url": "https://github.com/microsoft/semantic-kernel", "tool_type": "SDK"},
]


def sync_agent_tools_from_articles(db: Session, articles: list[RawArticle]) -> list[AgentTool]:
    synced: list[AgentTool] = []
    for article in articles:
        text = f"{article.title} {article.summary or ''} {article.url}"
        if article.category != "agent" and not is_agent_related(text):
            continue
        if "github.com" not in article.url:
            continue
        stars = None
        m = re.search(r"\((\d+)\s*stars?\)", article.title, re.I)
        if m:
            stars = int(m.group(1))
        existing = db.query(AgentTool).filter(AgentTool.url == article.url).first()
        if existing:
            existing.name = (article.title_zh or article.title)[:200]
            existing.name_zh = article.title_zh or article.title[:200]
            existing.description = article.summary_zh or article.summary
            existing.description_zh = article.summary_zh or article.summary
            existing.article_id = article.id
            if stars:
                existing.stars = stars
            synced.append(existing)
            continue
        tool = AgentTool(
            name=(article.title_zh or article.title)[:200],
            name_zh=article.title_zh or article.title[:200],
            url=article.url,
            description=article.summary_zh or article.summary,
            description_zh=article.summary_zh or article.summary,
            tool_type="开源项目",
            stars=stars,
            article_id=article.id,
        )
        db.add(tool)
        synced.append(tool)
    db.commit()
    return synced


def seed_known_agent_tools(db: Session) -> int:
    added = 0
    for item in KNOWN_AGENT_TOOLS:
        if db.query(AgentTool).filter(AgentTool.url == item["url"]).first():
            continue
        db.add(AgentTool(
            name=item["name"],
            name_zh=item["name"],
            url=item["url"],
            tool_type=item["tool_type"],
            description_zh=f"{item['name']} - {item['tool_type']}类 Agent 工具",
        ))
        added += 1
    db.commit()
    return added
