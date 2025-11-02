import streamlit as st
import sys
import os
import time
import logging

# 配置 logging 输出到终端
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("Streamlit app started")

# 添加 main 目录到 Python 路径（必须在导入 main 模块之前）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'main'))
logger.info(f"Added path to sys.path: {os.path.join(os.path.dirname(__file__), 'main')}")

# 页面配置
st.set_page_config(page_title="崩铁：永劫回归", layout="wide")
st.title("🚀 永劫回归测试程序 - 实时流式版")

# 角色配置
CHARACTER_AVATARS = {
    "EpieiKeia216": "images/EpieiKeia216.png",  # 遐蝶
    "NeiKos496": "images/NeiKos496.png",  # 白厄
    "KaLos618": "images/KaLos618.png",  # 阿格莱雅
    "HapLotes405": "images/HapLotes405.png",  # 缇宝
    "PoleMos600": "images/PoleMos600.png",  # 万敌
    "HubRis504": "images/HubRis504.png",  # 刻律德菈
    "EleOs252": "images/EleOs252.png",  # 风堇
    "ApoRia432": "images/ApoRia432.png",  # 海瑟音
    "SkeMma720": "images/SkeMma720.png",  # 那刻夏
    "OreXis945": "images/OreXis945.png",  # 赛飞儿
    "Black_NeiKo": "images/Black_NeiKo.png",  # 盗火行者白厄
}

CHARACTER_NAMES = {
    "EpieiKeia216": "遐蝶",
    "NeiKos496": "白厄",
    "KaLos618": "阿格莱雅",
    "HapLotes405": "缇宝",
    "PoleMos600": "万敌",
    "HubRis504": "刻律德菈",
    "EleOs252": "风堇",
    "ApoRia432": "海瑟音",
    "SkeMma720": "那刻夏",
    "OreXis945": "赛飞儿",
    "Black_NeiKo": "盗火行者·白厄",
}

# 初始化 session_state
if 'events' not in st.session_state:
    st.session_state.events = []
    logger.info("Initialized events list")
if 'current_round' not in st.session_state:
    st.session_state.current_round = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
    logger.info("Initialized is_running to False")

# 侧边栏控制
with st.sidebar:
    st.header("⚙️ 控制面板")
    rounds = st.slider("选择迭代轮数", min_value=1, max_value=20, value=6)
    
    if st.button("🚀 开始永劫回归", type="primary", use_container_width=True):
        logger.info("Button '开始永劫回归' clicked")
        if not st.session_state.is_running:
            logger.info("Starting regression, rounds = %s", rounds)
            st.session_state.is_running = True
            st.session_state.events = []
            st.session_state.current_round = None
            st.session_state.generator_done = False  # 重置生成器状态
            st.session_state.event_generator = None  # 清空生成器
            st.session_state.processed_count = 0
            st.rerun()
        else:
            logger.warning("Already running!")
    
    if st.button("🔄 清空数据", use_container_width=True):
        st.session_state.events = []
        st.session_state.current_round = None
        st.session_state.is_running = False
        st.session_state.generator_done = False  # 重置生成器状态
        st.session_state.event_generator = None  # 清空生成器
        st.session_state.processed_count = 0
        st.rerun()
    
    st.divider()
    st.write(f"**已完成轮次:** {len([e for e in st.session_state.events if e['type'] == 'round_end'])} / {rounds}")
    st.write(f"**事件总数:** {len(st.session_state.events)}")

# 主界面
if st.session_state.is_running:
    logger.info("Entering is_running=True block")
    try:
        logger.info("Importing eternal_regression_realtime_streaming")
        from main import eternal_regression_realtime_streaming
        logger.info("Import successful")
        
        # 检查是否已经完成
        if st.session_state.event_generator is None:
            st.session_state.generator_done = False
        
        # 如果生成器未完成，获取下一个事件
        if not st.session_state.generator_done:
            if 'event_generator' not in st.session_state:
                # 第一次运行，创建生成器
                logger.info("Creating event generator for %s rounds", rounds)
                st.session_state.event_generator = eternal_regression_realtime_streaming(rounds=rounds)
                st.session_state.processed_count = 0
                logger.info("Generator created")
            
            try:
                # 获取一个事件
                logger.info("Getting next event, processed_count = %s", st.session_state.processed_count)
                event = next(st.session_state.event_generator)
                logger.info("Got event: %s", event['type'])
                st.session_state.events.append(event)
                st.session_state.processed_count += 1
                
                # 立即刷新显示
                st.rerun()
            except StopIteration:
                # 生成器已完成
                logger.info("Generator done, processed %s events", st.session_state.processed_count)
                st.session_state.generator_done = True
                st.session_state.is_running = False
                st.success("✅ 永劫回归测试完成！")
                st.rerun()
        
    except Exception as e:
        import traceback
        logger.error("Exception occurred: %s", str(e))
        logger.error(traceback.format_exc())
        st.error(f"执行出错: {str(e)}")
        st.exception(e)  # 显示完整错误堆栈
        st.session_state.is_running = False
        st.rerun()

# 显示实时流
if st.session_state.events:
    # 创建两个区域：左侧实时对话流，右侧角色状态
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.header("💬 实时对话流")
        
        # 显示所有对话事件
        for event in st.session_state.events:
            event_type = event['type']
            
            if event_type == 'oracle':
                with st.chat_message("缇宝", avatar=CHARACTER_AVATARS['HapLotes405']):
                    st.markdown(f"**神谕：** {event['message']}")
            
            elif event_type == 'fire_decision':
                decision_text = "✅ 逐火" if event['decision'] == '1' else "❌ 不逐火"
                char_name = CHARACTER_NAMES.get(event['char_id'], event['char_id'])
                with st.chat_message(char_name, avatar=CHARACTER_AVATARS.get(event['char_id'], "avatar_path")):
                    st.markdown(f"**{decision_text}**\n\n{event['message']}")
            
            elif event_type == 'persuasion':
                with st.chat_message("盗火行者·白厄", avatar=CHARACTER_AVATARS['Black_NeiKo']):
                    st.markdown(f"**盗火行者劝诫：** {event['message']}")
            
            elif event_type == 'handover_decision':
                decision_text = "✅ 交出火种" if event['decision'] == '1' else "❌ 拒绝交出"
                char_name = CHARACTER_NAMES.get(event['char_id'], event['char_id'])
                with st.chat_message(char_name, avatar=CHARACTER_AVATARS.get(event['char_id'], "avatar_path")):
                    st.markdown(f"**{decision_text}**\n\n{event['message']}")
            
            elif event_type == 'robbery':
                char_name = CHARACTER_NAMES.get(event['char_id'], event['char_id'])
                st.error(f"⚔️ **{char_name}** 的火种被强夺！")
    
    with col_right:
        st.header("📊 当前状态")
        
        # 找到最新的 round_end 事件来显示当前状态
        current_round_event = None
        for event in reversed(st.session_state.events):
            if event['type'] == 'round_end':
                current_round_event = event
                break
        
        if current_round_event:
            st.write(f"**当前轮次：第 {current_round_event['round_num']} 轮**")
            st.write("---")
            
            final_result = current_round_event['final_result']
            robbed_list = current_round_event['robbed_characters']
            
            # 统计
            total_fire = len([s for s in final_result.values() if '逐火' in s])
            willing = len([s for s in final_result.values() if '交出火种' in s])
            robbed = len([s for s in final_result.values() if '被强夺' in s])
            non_fire = len([s for s in final_result.values() if s == '不逐火'])
            
            st.metric("逐火者", total_fire)
            st.metric("主动交出", willing)
            st.metric("被强夺", robbed)
            st.metric("不逐火", non_fire)
            
            if robbed_list:
                st.error(f"被强夺：{', '.join([CHARACTER_NAMES.get(cid, cid) for cid in robbed_list])}")
            
            # 显示所有角色状态
            st.write("---")
            st.write("**所有角色状态：**")
            
            for char_id, status in final_result.items():
                char_name = CHARACTER_NAMES.get(char_id, char_id)
                
                if status == "不逐火":
                    st.write(f"⚪ {char_name}")
                elif "逐火_交出火种" in status:
                    st.write(f"✅ {char_name}")
                elif "逐火_不交出火种" in status:
                    st.write(f"🔥 {char_name}")
                elif "逐火_火种被强夺" in status:
                    st.write(f"⚔️ {char_name}")

else:
    st.info("👈 点击侧边栏的「开始永劫回归」按钮来启动测试")

# 底部显示完整历史
if len(st.session_state.events) > 0:
    with st.expander("📜 查看完整事件历史"):
        for i, event in enumerate(st.session_state.events):
            st.json(event)