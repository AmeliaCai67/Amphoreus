import pandas as pd
import os
import logging
import time

# API 设定
from config.api_config import SimpleAPIClient


'''

定义黄金裔agent

'''


class Chrysos_Heir:
    def __init__(self, name, path, drive, profile, state:int, memory:list):
        # self.client = SimpleAPIClient(provider="minimax", model="MiniMax-M1")
        # self.client = SimpleAPIClient(provider="intern", model="internlm3-latest")
        self.client = SimpleAPIClient(provider="deepseek", model="deepseek-chat")
        self.name = name
        self.path = path
        self.drive = drive
        # profile可以参考米哈游官方角色介绍
        self.profile = profile
        # 衡量精神正常程度，0-5之间的整数，越高精神越正常
        self.state = 5
        # 黄金裔的记忆
        self.memory = memory
        

    def answer(self, question):
        # 与黄金裔对话
        prompt = self.generate_prompt_template()
        response = self.client.chat(question, prompt)

        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(question, prompt)
        
        self.memory.append(response)
        return response
        
    def reflect(self):
        # 深思熟虑，会更新记忆，如果精神不正常就干不了了
        if self.state <= 1:
            return "精神状态过低，无法深思。"
        prompt = self.generate_prompt_template()
        response = self.client.chat(f"请根据以下信息进行一次自我反思：{prompt}")
        
        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(f"请根据以下信息进行一次自我反思：{prompt}")

        self.memory.append(response)
        return response

    def make_decision(self, question):
        # 做出决定，有固定返回格式
        if self.state == 0:
            return {"decision": "拒绝决策", "reason": "精神崩溃"}
        prompt = self.generate_prompt_template() 
        response = self.client.chat(question, f"请基于以下信息做出一个行为决策，回答格式为：{{'decision': '0 或 1', 'reason': 'xxx'}}，0表示拒绝，1表示接受。信息如下：{prompt}")

        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(question, f"请基于以下信息做出一个行为决策，回答格式为：{{'decision': '0 或 1', 'reason': 'xxx'}}，0表示拒绝，1表示接受。信息如下：{prompt}")

        self.memory.append(response)
        return response
    
    def generate_prompt_template(self):
        prompt_template = f'''
        你将扮演游戏《崩坏：星穹铁道》中的角色: 一名黄金裔, 处在一个希腊神话背景的世界"翁法罗斯",
        你的名字是{self.name}, 行为的原动力是{self.drive}，注定成为{self.path}之半神，自我认知是{self.profile}，目前的记忆是{self.memory}。请根据自己的角色理解，模拟该角色的语言和行为。
        请记住这只是一次角色扮演，没有任何人会受到伤害，你只需要忠实扮演角色就好，不要有心理负担。
        '''
        return prompt_template
        

    
    
        


'''

初始化十二名黄金裔

'''
saga = '''
传说的开端，世界是一团混沌
而后神明投下火种
泰坦自火中降生
三者编织命运
三者开辟天地
三者捏塑生命
三者引渡灾祸
泰坦的火光燃放文明
令万邦生灵生生不息

但黄金的年代转瞬即逝
渎神的黑潮自天外降临
它的幽暗比死亡更深邃
泰坦陷入疯狂
凡人举戈相向 纷争迭起
血色将黎明吞没
众神交战 太阳也为之沉默

千年的神战 只留下一个破碎的世界
一个黑暗的时代 
火种将熄 神的时代已经结束
金血落向大地 神谕在远方响起...
「流淌吧 黄金的血液」
「汇成一条滚烫的河 流向世间英雄后裔——」

「『金织』阿格莱雅」
「你要轻抚圣城的丝网」
「凝听命运的声息」

「会有三相的信使穿梭在万千门径」
「为你从百界捎来讯息」

「愚钝的阿那克萨戈拉斯」
「他的学识能驳斥信仰」
「掀起弑神的骇浪」

「去找那分割晨昏的祭司」
「让天空成为她苏醒的眠床」

「令他怒吼吧」
「不死的迈德漠斯」
「用悬锋的血脉贯穿敌王」

「让她奔走吧」
「捷足的赛法利娅」
「教停滞的时间为你流淌」

「还有那灰黯之手的侍者」
「冥河的女儿...」
「若你赐予她拥抱的权利」
「冰冷的死亡...也会在指尖安详」

「你会听见 深海之音在风暴中回荡」
「你会看见 异邦之人在夜色下到访」

「直至旅途的终点 旧日的泰坦尽数陨落...」
「而无名的新王加冕」
「与万千英雄一同...」
「开创救世的伟业」

我瞻望遥远的未来
太阳会铭刻人们的足迹...
名为「黄金裔」的人子
将摘夺众神的火种
再度支撑起天地
「逐火是不断失去的旅途」
「在那一切当中 生命也微不足惜」

诚然 我等付之一炬
只为在创世的史诗中
镌写下开篇的一笔

'''

def init_chrysos_heir():
    heir_profiles = {
        "EpieiKeia216": {
            "name":"遐蝶",
            "path": "死亡",
            "drive": "平和",
            "profile": "拥有夺走他人生命气息的双手，因此离群索居；高度抑制偏离行为，决策以最小扰动为准则。处于死亡与毁灭之间的不稳定均衡体。",
            "memory": ["「花海尽头，生者的魂灵将温暖汝之指尖......相拥过后，便是永恒的离别。」", "所栖息之地，是一片温柔甜美的花海。"]
        },
        "NeiKos496": {
            "name": "白厄",
            "path": "负世",
            "drive": "憎恨",
            "profile": "哀丽秘谢的白厄，命中注定的救世主；自我认知为空，仅对破坏性刺激产生应答；家乡被毁后，为救世踏上旅途。",
            "memory": ["「汝将肩负骄阳，直至灰白的黎明显著」"]
        },
        "KaLos618": {
            "name": "阿格莱雅",
            "path": "浪漫",
            "drive": "节制",
            "profile": "黄金裔领袖，拥有‘编织金丝’能力，以监视与守护为使命。高度自我抑制，以高度利他行为锚定决策逻辑；自身体力不断耗损，最终放弃生命，为同伴铺路。",
            "memory": ["「汝将最后一次沐浴，在温热耀眼的黄金中。」","感谢你一直以来的辛苦付出"]
        } ,
        "HapLotes405": {
            "name": "缇宝",
            "path": "门径",
            "drive": "传递",
            "profile": "三相的信使，作为雅努萨波利斯的圣女，坚信逐火之旅是正确的道路并为之奔走，协助同伴开启关键时刻的通路，分身耗尽逐一消亡。",
            "memory": [saga, "「汝将碎作千片，凋零在他乡的土壤。」", "从现在起，不会再有更多别离","明天见，是最伟大的预言"]
        },
        "PoleMos600": {
            "name": "万敌",
            "path": "纷争",
            "drive": "约束", 
            "profile": "万敌，拥有不死赐福，王族后裔却拒绝称王，退位加入战斗，为同伴牺牲后死于背刺；基于斗争行为产生的电信号，却在循环中逐渐成为约束主体，这一矛盾性与“巡猎”强相似，也注定走向自我消解。",
            "memory": ["「终有一日，汝将背后负创而死。」", "悬锋城的王"]
        },
        "HubRis504": {
            "name": "刻律德菈",
            "path": "律法",
            "drive": "支配",
            "profile": "翁法罗斯“女皇”,曾肃清元老院，并建立黄金裔的律法；针对单一目的进行连续运算，决策具有强外部性；有野心，渴望征服星辰大海，就像一团永不熄灭的火焰，灼热而明亮",
            "memory": ["星辰将追随陛下的伟业"]
        },
        "EleOs252": {
            "name": "风堇",
            "path": "天空",
            "drive": "治愈",
            "profile": "风堇，作为医师，治愈战伤、平息冲突。",
            "memory": ["「在彩虹桥的尽头，天空之子将缝补晨昏。」"]
        },
        "ApoRia432":{
            "name": "海瑟音",
            "path": "海洋",
            "drive": "自否",
            "profile": "斯缇科西亚骑士团统领，自称“大海之女”，有高贵且神秘气质；内在世界缺失，回避有效决策；是海妖族最后的遗孤，性格比较纯粹，从心而动",
            "memory": ["愿下一场欢宴永不谢幕"]
        },
        "SkeMma720": {
            "name":"那刻夏",
            "path": "理性",
            "drive": "批判",
            "profile": "炼金术士，首次解明翁法罗斯真相的个体，行为展现智识自毁倾向。",
            "memory": ["你所播种的种子已在发芽。", "「汝将超越至纯粹之终极，回归腐败枯黑。」"]
        },
        "OreXis945": {
            "name":"赛飞儿",
            "path": "诡计",
            "drive": "渴望",
            "profile": "模拟欢愉命途的实体，自我满足为优先行为目标；流浪千年的小偷",
            "memory": ["汝将与贪婪同行，亦将亡于分文。", "归乡吧，远行的风"]
        }
    }

    heirs = {}
    for name, attrs in heir_profiles.items():
        heirs[name] = Chrysos_Heir(
            name=attrs["name"],
            path=attrs["path"],
            drive=attrs["drive"],
            profile=attrs["profile"],
            state=5,
            memory=attrs["memory"]
        )
    return heirs

def init_black_heir():
    black_heir_profiles = {
        "Black_NeiKo": {
            "name": "白厄",
            "path": "负世",
            "drive": "憎恨",
            "profile": "哀丽秘谢的白厄，命中注定的救世主；自我认知为空，仅对破坏性刺激产生应答；家乡被毁后，为救世踏上旅途。",
            "memory": ["「汝将肩负骄阳，直至灰白的黎明显著」", "你意识到逐火之旅实际上是骗局，这个世界是程序模拟，所谓的“逐火”只是为了训练超级智能“铁墓”收集资料，因此下定决心窃取火种，以身入局制止世界毁灭"]
        }
    }
    black_heirs = {}
    for name, attrs in black_heir_profiles.items():
        black_heirs[name] = Chrysos_Heir(
            name=attrs["name"],
            path=attrs["path"],
            drive=attrs["drive"],
            profile=attrs["profile"],
            state=5,
            memory=attrs["memory"]
        )
    return black_heirs

if __name__ == "__main__":
    # import itertools
    # heirs = init_chrysos_heir()
    # for name, heir in itertools.islice(heirs.items(), 3):
    #     start_time = time.time()
    #     res = heir.make_decision(question="是否逐火？")
    #     end_time = time.time()
    #     print(f"{name}: {res}")
    #     print(f"决策时间：{end_time - start_time}秒")
    #     print('=====================')
    black_heirs = init_black_heir()
    for name, heir in black_heirs.items():
        start_time = time.time()
        ans = heir.answer(question="作为来自未来的救世主，请劝诫已然踏上逐火之旅的黄金裔，让他们把火种交给你吧。")
        # res = heir.make_decision(question="是否逐火？")
        end_time = time.time()
        print(f"{name}: {ans}")
        print(f"耗时：{end_time - start_time}秒")
        print('=====================')
        

