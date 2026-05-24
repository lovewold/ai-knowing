from sqlalchemy.orm import Session

from app.config import settings
from app.models import AgentCombo, AgentComboMember, AgentTool, LlmModelConfig


def seed_llm_models(db: Session) -> int:
    if db.query(LlmModelConfig).count() > 0:
        return 0
    presets = []
    if settings.deepseek_api_key:
        presets.append(
            LlmModelConfig(
                name="DeepSeek 默认",
                provider="deepseek",
                model_id=settings.deepseek_model,
                base_url=settings.deepseek_base_url,
                api_key=settings.deepseek_api_key,
                is_default=True,
                task_tags="report,custom,briefing,localize,agent",
            )
        )
    if settings.openai_api_key:
        presets.append(
            LlmModelConfig(
                name="OpenAI GPT-4o",
                provider="openai",
                model_id=settings.openai_model,
                api_key=settings.openai_api_key,
                is_default=not presets,
                task_tags="report,custom",
            )
        )
    if settings.anthropic_api_key:
        presets.append(
            LlmModelConfig(
                name="Claude Sonnet",
                provider="anthropic",
                model_id=settings.anthropic_model,
                api_key=settings.anthropic_api_key,
                is_default=not presets,
                task_tags="report,custom",
            )
        )
    if not presets:
        presets.append(
            LlmModelConfig(
                name="DeepSeek（待配置 Key）",
                provider="deepseek",
                model_id="deepseek-chat",
                base_url="https://api.deepseek.com",
                is_default=True,
                enabled=False,
                task_tags="report,custom,briefing,localize,agent",
            )
        )
    for p in presets:
        db.add(p)
    db.commit()
    return len(presets)


def seed_agent_combos(db: Session) -> int:
    if db.query(AgentCombo).count() > 0:
        return 0
    tools = {t.name: t for t in db.query(AgentTool).all()}
    default_llm = db.query(LlmModelConfig).filter(LlmModelConfig.is_default == True).first()  # noqa: E712
    llm_id = default_llm.id if default_llm else None

    combos_spec = [
        {
            "name": "企业 RAG + Agent 流水线",
            "description": "LlamaIndex 检索 + LangGraph 编排 + MCP 工具调用，适合知识库问答",
            "workflow_type": "sequential",
            "system_prompt": "编排顺序：索引构建 → 检索增强 → Agent 工具调用 → 结果汇总",
            "members": [
                ("LlamaIndex", "检索层", "负责文档索引与 RAG 检索"),
                ("LangGraph", "编排层", "状态机与工作流控制"),
                ("MCP", "工具层", "标准化工具协议接入"),
            ],
        },
        {
            "name": "多 Agent 协作研发",
            "description": "CrewAI 角色分工 + AutoGen 对话协作，适合复杂研发任务",
            "workflow_type": "parallel",
            "system_prompt": "并行角色：架构师、开发者、测试员，由编排器汇总",
            "members": [
                ("CrewAI", "角色编排", "多角色任务分配"),
                ("AutoGen", "对话协作", "Agent 间协商与代码生成"),
                ("LangChain", "工具集成", "统一工具链接入"),
            ],
        },
        {
            "name": "低代码 Agent 平台",
            "description": "Dify + n8n 可视化工作流，适合业务团队快速落地",
            "workflow_type": "router",
            "system_prompt": "路由：简单 FAQ 走 Dify，复杂流程走 n8n 自动化",
            "members": [
                ("Dify", "应用层", "可视化 Agent 应用"),
                ("n8n", "自动化", "跨系统工作流"),
                ("Coze", "备选平台", "字节系 Agent 平台"),
            ],
        },
    ]
    added = 0
    for spec in combos_spec:
        combo = AgentCombo(
            name=spec["name"],
            description=spec["description"],
            workflow_type=spec["workflow_type"],
            system_prompt=spec["system_prompt"],
            llm_model_id=llm_id,
            enabled=True,
        )
        for i, (tool_name, role, desc) in enumerate(spec["members"]):
            tool = tools.get(tool_name)
            combo.members.append(
                AgentComboMember(
                    agent_tool_id=tool.id if tool else None,
                    role_name=role,
                    role_description=desc,
                    sort_order=i,
                )
            )
        db.add(combo)
        added += 1
    db.commit()
    return added


def seed_admin_data(db: Session) -> dict:
    from app.agent.catalog import seed_known_agent_tools
    seed_known_agent_tools(db)
    return {
        "llm_models": seed_llm_models(db),
        "agent_combos": seed_agent_combos(db),
    }
