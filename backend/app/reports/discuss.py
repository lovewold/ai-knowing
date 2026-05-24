"""Research-oriented dialogue on report content."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.llm.resolver import get_llm_provider
from app.models import Report
from app.reports.citations import citations_from_json

RESEARCH_SYSTEM = """你是 AI全知 的「研究导师」。用户正在阅读一份 AI 行业/技术报告，你的任务是通过对话帮助学习者：

1. 澄清与收窄研究方向（问题、假设、边界）
2. 提出 2–3 个可验证的后续研究问题或实验路径
3. 对比不同技术路线的优劣与适用场景
4. 给出可执行的下一步（阅读、工具、小实验、访谈对象等）

风格：中文、专业但易懂、结构化（可用小标题与列表）。每次回答控制在 400 字以内，除非用户要求展开。
若报告信息不足，诚实说明并给出通用研究框架建议。鼓励批判性思考，避免空泛 praise。"""

FOLLOWUP_HINT = """
在回答末尾另起一行，以「建议追问：」开头，给出 2 个简短的后续问题（用分号分隔，不要编号）。"""


def _strip_refs(md: str) -> str:
    import re

    return re.sub(r"\n##\s*参考来源[\s\S]*$", "", md, flags=re.M).strip()


def _format_history(history: list[dict]) -> str:
    lines: list[str] = []
    for turn in history[-8:]:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        label = "用户" if role == "user" else "导师"
        lines.append(f"{label}：{content[:800]}")
    return "\n".join(lines)


async def discuss_report(
    db: Session,
    report: Report,
    message: str,
    history: list[dict] | None = None,
) -> dict:
    history = history or []
    body = _strip_refs(report.content_md or "")[:14000]
    citations = citations_from_json(report.citations_json)
    cite_lines = "\n".join(f"- {c.title}: {c.url}" for c in citations[:8])

    user_block = f"""## 报告标题
{report.title}

## 用户原始需求
{report.user_prompt or '（无）'}

## 报告正文（节选）
{body}

## 参考链接
{cite_lines or '（无）'}

## 对话历史
{_format_history(history) or '（首次对话）'}

## 本轮问题
{message.strip()}
"""

    llm = get_llm_provider(task="report", db=db)
    raw = await llm.generate(RESEARCH_SYSTEM + FOLLOWUP_HINT, user_block)
    reply = raw.strip()

    suggestions: list[str] = []
    if "建议追问：" in reply:
        main, tail = reply.split("建议追问：", 1)
        reply = main.strip()
        suggestions = [s.strip() for s in tail.replace("；", ";").split(";") if s.strip()][:3]

    if not suggestions:
        suggestions = [
            "帮我列出 3 个可验证的研究假设",
            "如果资源有限，优先做哪条路径？",
        ]

    return {"reply": reply, "suggestions": suggestions}
