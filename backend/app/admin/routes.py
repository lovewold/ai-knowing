import yaml
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import (
    AgentCombo,
    AgentComboMember,
    AgentTool,
    DailyBriefing,
    LlmModelConfig,
    RawArticle,
    Report,
    SignalScore,
)
from app.yaml_config import (
    DailyBriefingConfig,
    DouyinCreator,
    SourceConfig,
    get_config_dir,
    load_all_sources,
    load_daily_briefing_yaml,
    load_douyin_creators,
    load_scoring_config,
    load_sources,
    save_daily_briefing_yaml,
    save_douyin_creators_yaml,
    save_sources_yaml,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(x_admin_token: str | None = Header(default=None)):
    if settings.admin_token and x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="无效的管理员 Token")


def _mask_key(key: str | None) -> str | None:
    if not key:
        return None
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


def _model_dict(m: LlmModelConfig, mask: bool = True) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "provider": m.provider,
        "model_id": m.model_id,
        "base_url": m.base_url,
        "api_key": _mask_key(m.api_key) if mask else m.api_key,
        "has_api_key": bool(m.api_key),
        "is_default": m.is_default,
        "enabled": m.enabled,
        "task_tags": m.task_tags,
        "max_tokens": m.max_tokens,
        "temperature": m.temperature,
        "created_at": m.created_at.isoformat(),
        "updated_at": m.updated_at.isoformat(),
    }


def _combo_dict(c: AgentCombo) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "workflow_type": c.workflow_type,
        "llm_model_id": c.llm_model_id,
        "llm_model_name": c.llm_model.name if c.llm_model else None,
        "system_prompt": c.system_prompt,
        "enabled": c.enabled,
        "members": [
            {
                "id": m.id,
                "agent_tool_id": m.agent_tool_id,
                "tool_name": m.agent_tool.name if m.agent_tool else None,
                "role_name": m.role_name,
                "role_description": m.role_description,
                "sort_order": m.sort_order,
            }
            for m in sorted(c.members, key=lambda x: x.sort_order)
        ],
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
    }


class LlmModelCreate(BaseModel):
    name: str
    provider: str
    model_id: str
    base_url: str | None = None
    api_key: str | None = None
    is_default: bool = False
    enabled: bool = True
    task_tags: str = "report,custom,briefing,localize,agent"
    max_tokens: int = 4096
    temperature: float = 0.3


class LlmModelUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    model_id: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    is_default: bool | None = None
    enabled: bool | None = None
    task_tags: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None


class ComboMemberIn(BaseModel):
    agent_tool_id: int | None = None
    role_name: str
    role_description: str | None = None
    sort_order: int = 0


class AgentComboCreate(BaseModel):
    name: str
    description: str | None = None
    workflow_type: str = "sequential"
    llm_model_id: int | None = None
    system_prompt: str | None = None
    enabled: bool = True
    members: list[ComboMemberIn] = Field(default_factory=list)


class AgentComboUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    workflow_type: str | None = None
    llm_model_id: int | None = None
    system_prompt: str | None = None
    enabled: bool | None = None
    members: list[ComboMemberIn] | None = None


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    return {
        "articles": db.query(RawArticle).count(),
        "reports": db.query(Report).count(),
        "high_signal": db.query(SignalScore).filter(SignalScore.status == "high").count(),
        "agent_tools": db.query(AgentTool).count(),
        "briefings": db.query(DailyBriefing).count(),
        "llm_models": db.query(LlmModelConfig).count(),
        "agent_combos": db.query(AgentCombo).count(),
        "sources": len(load_sources()),
    }


@router.get("/models")
def list_models(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    models = db.query(LlmModelConfig).order_by(LlmModelConfig.is_default.desc(), LlmModelConfig.id).all()
    return [_model_dict(m) for m in models]


@router.post("/models")
def create_model(body: LlmModelCreate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    if body.is_default:
        db.query(LlmModelConfig).update({LlmModelConfig.is_default: False})
    m = LlmModelConfig(**body.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _model_dict(m)


@router.put("/models/{model_id}")
def update_model(model_id: int, body: LlmModelUpdate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    m = db.query(LlmModelConfig).filter(LlmModelConfig.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404)
    data = body.model_dump(exclude_unset=True)
    if data.get("is_default"):
        db.query(LlmModelConfig).filter(LlmModelConfig.id != model_id).update({LlmModelConfig.is_default: False})
    if "api_key" in data and data["api_key"] is None:
        del data["api_key"]
    for k, v in data.items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return _model_dict(m)


@router.delete("/models/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    m = db.query(LlmModelConfig).filter(LlmModelConfig.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404)
    if m.is_default:
        raise HTTPException(status_code=400, detail="不能删除默认模型，请先设置其他模型为默认")
    db.delete(m)
    db.commit()
    return {"ok": True}


@router.get("/agent-combos")
def list_combos(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    combos = (
        db.query(AgentCombo)
        .options(joinedload(AgentCombo.members).joinedload(AgentComboMember.agent_tool), joinedload(AgentCombo.llm_model))
        .order_by(AgentCombo.id)
        .all()
    )
    return [_combo_dict(c) for c in combos]


@router.post("/agent-combos")
def create_combo(body: AgentComboCreate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    combo = AgentCombo(
        name=body.name,
        description=body.description,
        workflow_type=body.workflow_type,
        llm_model_id=body.llm_model_id,
        system_prompt=body.system_prompt,
        enabled=body.enabled,
    )
    for mem in body.members:
        combo.members.append(AgentComboMember(**mem.model_dump()))
    db.add(combo)
    db.commit()
    db.refresh(combo)
    combo = (
        db.query(AgentCombo)
        .options(joinedload(AgentCombo.members).joinedload(AgentComboMember.agent_tool), joinedload(AgentCombo.llm_model))
        .filter(AgentCombo.id == combo.id)
        .first()
    )
    return _combo_dict(combo)


@router.put("/agent-combos/{combo_id}")
def update_combo(combo_id: int, body: AgentComboUpdate, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    combo = db.query(AgentCombo).filter(AgentCombo.id == combo_id).first()
    if not combo:
        raise HTTPException(status_code=404)
    data = body.model_dump(exclude_unset=True)
    members = data.pop("members", None)
    for k, v in data.items():
        setattr(combo, k, v)
    if members is not None:
        combo.members.clear()
        db.flush()
        for mem in members:
            combo.members.append(AgentComboMember(**mem))
    db.commit()
    combo = (
        db.query(AgentCombo)
        .options(joinedload(AgentCombo.members).joinedload(AgentComboMember.agent_tool), joinedload(AgentCombo.llm_model))
        .filter(AgentCombo.id == combo_id)
        .first()
    )
    return _combo_dict(combo)


@router.delete("/agent-combos/{combo_id}")
def delete_combo(combo_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    combo = db.query(AgentCombo).filter(AgentCombo.id == combo_id).first()
    if not combo:
        raise HTTPException(status_code=404)
    db.delete(combo)
    db.commit()
    return {"ok": True}


@router.get("/config/sources")
def get_sources_config(_: None = Depends(verify_admin)):
    return [s.model_dump(exclude_none=True) for s in load_all_sources()]


@router.put("/config/sources")
def put_sources_config(sources: list[SourceConfig], _: None = Depends(verify_admin)):
    payload = [s.model_dump(exclude_none=True) for s in sources]
    save_sources_yaml(payload)
    return {"ok": True, "count": len(sources)}


@router.get("/config/daily-briefing")
def get_briefing_config(_: None = Depends(verify_admin)):
    return load_daily_briefing_yaml()


@router.put("/config/daily-briefing")
def put_briefing_config(config: DailyBriefingConfig, _: None = Depends(verify_admin)):
    save_daily_briefing_yaml(config.model_dump())
    return {"ok": True}


@router.get("/config/douyin-creators")
def get_creators_config(_: None = Depends(verify_admin)):
    return [c.model_dump() for c in load_douyin_creators()]


@router.put("/config/douyin-creators")
def put_creators_config(creators: list[DouyinCreator], _: None = Depends(verify_admin)):
    payload = [c.model_dump() for c in creators]
    save_douyin_creators_yaml(payload)
    return {"ok": True, "count": len(creators)}


@router.get("/config/scoring")
def get_scoring_config(_: None = Depends(verify_admin)):
    return load_scoring_config().model_dump()


@router.get("/tools")
def list_tools_for_admin(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    tools = db.query(AgentTool).order_by(AgentTool.name).all()
    return [{"id": t.id, "name": t.name_zh or t.name, "tool_type": t.tool_type, "url": t.url} for t in tools]
