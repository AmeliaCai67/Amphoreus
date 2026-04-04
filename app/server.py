import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

# 允许前端跨域请求（本地开发时 Vue 通常在 5173 端口，FastAPI 在 8000 端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境记得改成你真实的域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义前端传过来的配置参数
class GameConfig(BaseModel):
    password: str
    max_iterations: int = 6
    max_persuasions: int = 3

# 核心改造：把你原来的 main 函数变成一个 async 生成器 (Generator)
async def run_game_stream(config: GameConfig):
    # 1. 简单的密码校验
    if config.password != "Amphoreus2026": # 这里设置你的专属密码
        yield "data: 【系统拦截】访问口令错误，神谕未响应。\n\n"
        return
        
    # 2. 游戏开始前的初始化
    yield "data: 🚀 启动永劫回归测试程序\n\n"
    await asyncio.sleep(0.5) # 稍微停顿，让前端有逐行打印的视觉效果
    yield f"data: === 开始永劫回归测试，共 {config.max_iterations} 轮迭代 ===\n\n"
    
    # 3. 把你原来的循环搬进来
    for iteration in range(1, config.max_iterations + 1):
        yield f"data: 🔄 第 {iteration} 轮永劫回归开始\n\n"
        yield f"data: ----------------------------------------\n\n"
        
        # --- 这里填入你原来调用神谕、角色决策的代码 ---
        # 假设你原来是： print(f"EpieiKeia216: {decision_json}")
        # 现在改成： yield f"data: EpieiKeia216: {decision_json}\n\n"
        
        # 模拟调用大模型 API 的耗时 (实际代码中如果是同步 requests，建议改成 httpx 异步请求)
        await asyncio.sleep(1.5) 
        yield 'data: EpieiKeia216: {"decision": "0", "reason": "我双手的气息会夺走生命之火..."}\n\n'
        
        # --- 这里填入你原来劝说阶段的代码 ---
        for persuasion in range(1, config.max_persuasions + 1):
            yield f"data: === 第 {persuasion} 次劝说 ===\n\n"
            await asyncio.sleep(1)
            
    # 4. 结束标志，告诉前端不用再等了
    yield "data: [DONE]\n\n"


# 对外暴露的 API 接口
@app.post("/api/run_game")
async def start_game_endpoint(config: GameConfig):
    # 关键点：返回 StreamingResponse，并指定 media_type 为 text/event-stream
    return StreamingResponse(run_game_stream(config), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # 在终端运行这个脚本，服务就会启动在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)