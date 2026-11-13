from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/coach", tags=["coach"])


@router.post("/analyze")
def analyze_player():
    """生成教练分析（占位，待实现）。"""
    return JSONResponse(status_code=501, content={"detail": "Not Implemented"})


@router.get("/plan/{riot_id}")
def get_improvement_plan(riot_id: str):
    """获取改进计划（占位，待实现）。"""
    return JSONResponse(status_code=501, content={"detail": "Not Implemented"})
