import asyncio
import sys
import os
from typing import Optional

# 添加 main 目录到模块搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'main'))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入 main 模块的函数
import main
import interactive_game as ig

app = FastAPI()

# 允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境记得改成你真实的域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义配置参数模型（用于文档）
class GameConfig(BaseModel):
    max_iterations: int = 6
    max_persuasions: int = 3


# ===== 交互式玩家扮演模式 =====

class InteractiveGameConfig(BaseModel):
    max_rounds: int = 1


class ChooseCharacterRequest(BaseModel):
    char_id: str


class DecisionRequest(BaseModel):
    decision: str  # "1" 表示接受/逐火/交出，"0" 表示拒绝
    reason: Optional[str] = None


def extract_reason_from_message(message: str) -> str:
    """
    从消息中提取 reason 字段
    如果消息是 JSON 格式且包含 reason 字段，则返回 reason 的内容
    否则返回原消息
    """
    if not message or not isinstance(message, str):
        return message or ""
    
    message = message.strip()
    
    # 检查是否是 JSON 格式（以 { 开头）
    if message.startswith('{') and 'reason' in message:
        try:
            import json
            import re
            
            # 尝试提取 reason 字段的值
            # 匹配 'reason': '...' 或 "reason": "..." 格式
            pattern = r"['\"]reason['\"]\s*:\s*['\"](.+?)['\"](?:,|\})"
            match = re.search(pattern, message, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # 如果正则提取失败，尝试 json 解析
            try:
                data = json.loads(message)
                if isinstance(data, dict) and 'reason' in data:
                    return str(data['reason']).strip()
            except json.JSONDecodeError:
                pass
                
        except Exception:
            pass
    
    return message


async def run_game_stream(max_iterations: int = 6, max_persuasions: int = 3):
    """
    运行永劫回归游戏流
    
    调用 main.py 中的 eternal_regression_realtime_streaming 函数，
    将生成器产生的事件转换为 SSE 格式返回给前端
    """
    # 启动游戏流
    yield "data: >>> 启动永劫回归测试程序\n\n"
    yield f"data: >>> === 开始永劫回归测试，共 {max_iterations} 轮迭代 ===\n\n"
    
    try:
        # 调用 main.py 的流式生成器
        event_generator = main.eternal_regression_realtime_streaming(
            rounds=max_iterations,
            max_persuasion_attempts=max_persuasions
        )
        
        # 遍历所有事件并转换为 SSE 格式
        for event in event_generator:
            event_type = event.get('type', '')
            
            if event_type == 'start':
                # 游戏开始
                pass  # 已在上面输出
                
            elif event_type == 'round_start':
                round_num = event.get('round_num', 0)
                yield f"data: >>> [第 {round_num} 轮永劫回归开始]\n\n"
                yield f"data: ----------------------------------------\n\n"
            
            elif event_type == 'oracle':
                char_name = event.get('char_name', '未知角色')
                message = event.get('message', '')
                yield f"data: >>> [{char_name}] 发布神谕:\n"
                yield f"data: {message}\n\n"
            
            elif event_type == 'fire_decision':
                char_name = event.get('char_name', '未知角色')
                decision = event.get('decision', '')
                message = event.get('message', '')
                decision_text = "逐火" if decision == '1' else "不逐火"
                # 提取 reason 字段
                reason_text = extract_reason_from_message(message)
                yield f"data: >>> [{char_name}] 决定: {decision_text}\n"
                yield f"data:    理由: {reason_text[:200]}{'...' if len(reason_text) > 200 else ''}\n\n"
            
            elif event_type == 'fire_result':
                result = event.get('result', {})
                fire_chasers = [name for name, status in result.items() if status == '逐火']
                yield f"data: >>> 逐火者: {', '.join(fire_chasers)}\n\n"
            
            elif event_type == 'persuasion':
                char_name = event.get('char_name', '未知角色')
                message = event.get('message', '')
                yield f"data: >>> [{char_name}] 劝说道:\n"
                yield f"data: {message[:300]}{'...' if len(message) > 300 else ''}\n\n"
            
            elif event_type == 'handover_decision':
                char_name = event.get('char_name', '未知角色')
                decision = event.get('decision', '')
                message = event.get('message', '')
                decision_text = "交出火种" if decision == '1' else "拒绝交出"
                # 提取 reason 字段
                reason_text = extract_reason_from_message(message)
                yield f"data: >>> [{char_name}] 回应: {decision_text}\n"
                yield f"data:    理由: {reason_text[:200]}{'...' if len(reason_text) > 200 else ''}\n\n"
            
            elif event_type == 'persuasion_attempt':
                attempt = event.get('attempt', 0)
                targets = event.get('targets', [])
                yield f"data: >>> === 第 {attempt} 次劝说 ===\n"
                yield f"data:    目标: {', '.join(targets)}\n\n"
            
            elif event_type == 'persuasion_detail':
                persuader_name = event.get('persuader_name', '未知')
                target_name = event.get('target_name', '未知')
                message = event.get('message', '')
                yield f"data: >>> [{persuader_name}] 劝说 [{target_name}]:\n"
                yield f"data: {message[:250]}{'...' if len(message) > 250 else ''}\n\n"
            
            elif event_type == 'handover_redecision':
                char_name = event.get('char_name', '未知角色')
                decision = event.get('decision', '')
                decision_text = "改变主意，交出火种" if decision == '1' else "仍然拒绝"
                yield f"data: >>> [{char_name}] {decision_text}\n\n"
            
            elif event_type == 'robbery':
                char_name = event.get('char_name', '未知角色')
                yield f"data: >>> [{char_name}] 的火种被强夺！\n\n"
            
            elif event_type == 'round_end':
                round_num = event.get('round_num', 0)
                final_result = event.get('final_result', {})
                robbed = event.get('robbed_characters', [])
                memory_count = event.get('memory_count', {})
                
                yield f"data: >>> [第 {round_num} 轮结果统计]\n"
                for char_id, status in final_result.items():
                    yield f"data:    {char_id}: {status}\n"
                if robbed:
                    yield f"data:    被强夺: {', '.join(robbed)}\n"
                for bid, count in memory_count.items():
                    yield f"data:    {bid} 记忆条数: {count}\n"
                yield f"data: ----------------------------------------\n\n"
            
            elif event_type == 'complete':
                total_rounds = event.get('total_rounds', 0)
                yield f"data: >>> 永劫回归测试完成！共执行 {total_rounds} 轮迭代\n\n"
            
            # 让出控制权，避免阻塞
            await asyncio.sleep(0.01)
    
    except Exception as e:
        yield f"data: >>> 发生错误: {str(e)}\n\n"
    
    # 结束标志
    yield "data: [DONE]\n\n"


@app.get("/api/run_game")
async def start_game_endpoint(
    max_iterations: int = 6,
    max_persuasions: int = 3
):
    """
    对外暴露的 API 接口 (GET)
    
    参数:
    - max_iterations: 迭代次数，默认6
    - max_persuasions: 最大劝说次数，默认3
    
    返回 StreamingResponse，media_type 为 text/event-stream
    """
    return StreamingResponse(
        run_game_stream(max_iterations, max_persuasions),
        media_type="text/event-stream"
    )


# ===== 交互式玩家扮演模式 API =====

@app.post("/api/game/create")
async def create_interactive_game(config: InteractiveGameConfig):
    """
    创建一局交互式游戏会话
    
    参数:
    - max_rounds: 最大回合数，默认1
    
    返回:
    - session_id: 会话ID
    - stage: 当前阶段 (created)
    """
    session_id = ig.create_session(max_rounds=config.max_rounds)
    return {
        "session_id": session_id,
        "stage": "created",
        "message": "游戏会话已创建，调用 /api/game/{session_id}/start 开始",
    }


@app.post("/api/game/{session_id}/start")
async def start_interactive_game(session_id: str):
    """
    开始游戏：返回开场文案、神谕和可选角色列表
    """
    session = ig.get_session(session_id)
    return session.start()


@app.post("/api/game/{session_id}/choose")
async def choose_character(session_id: str, req: ChooseCharacterRequest):
    """
    玩家选择扮演的角色
    
    参数:
    - char_id: 角色ID（不能是缇宝 HapLotes405）
    """
    session = ig.get_session(session_id)
    return session.choose_character(req.char_id)


@app.post("/api/game/{session_id}/fire_decision")
async def submit_fire_decision(session_id: str, req: DecisionRequest):
    """
    玩家提交逐火决策
    
    当玩家初次选择不逐火时，缇宝和阿格莱雅会劝说一轮，
    此时 stage 变为 "fire_persuasion"，前端需再次调用本接口提交二次决策。
    
    参数:
    - decision: "1" 表示逐火，"0" 表示不逐火
    - reason: 决策理由（可选，不填由AI生成）
    """
    session = ig.get_session(session_id)
    return session.submit_fire_decision(req.decision, req.reason)


@app.post("/api/game/{session_id}/handover_decision")
async def submit_handover_decision(session_id: str, req: DecisionRequest):
    """
    玩家提交交火种决策
    
    若玩家拒绝交出火种，盗火行者会劝说一轮，stage 变为 "handover_persuasion"，
    前端需调用 /api/game/{session_id}/handover_redecision 提交二次决策。
    
    参数:
    - decision: "1" 表示交出火种，"0" 表示拒绝
    - reason: 决策理由（可选，不填由AI生成）
    """
    session = ig.get_session(session_id)
    return session.submit_handover_decision(req.decision, req.reason)


@app.post("/api/game/{session_id}/handover_redecision")
async def submit_handover_redecision(session_id: str, req: DecisionRequest):
    """
    盗火行者劝说后，玩家再次提交交火种决策
    
    参数:
    - decision: "1" 表示改变主意交出火种，"0" 表示仍然拒绝
    - reason: 决策理由（可选，不填由AI生成）
    """
    session = ig.get_session(session_id)
    return session.submit_handover_redecision(req.decision, req.reason)


@app.post("/api/game/{session_id}/continue")
async def continue_interactive_game(session_id: str):
    """
    回合结束后继续下一回合，或结束游戏
    """
    session = ig.get_session(session_id)
    return session.continue_game()


@app.get("/api/game/{session_id}/state")
async def get_interactive_game_state(session_id: str):
    """
    获取当前游戏状态
    """
    session = ig.get_session(session_id)
    return session._state_response()


if __name__ == "__main__":
    import uvicorn
    # 在终端运行这个脚本，服务就会启动在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
