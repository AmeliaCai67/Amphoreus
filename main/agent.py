import time

# API 设定
from config.api_config import SimpleAPIClient
from prompt_manager import get_prompt_manager


'''

定义黄金裔agent

'''


class Chrysos_Heir:
    def __init__(self, char_id, client_provider="deepseek", client_model="deepseek-chat"):
        """
        初始化黄金裔 Agent

        Args:
            char_id: 角色唯一 ID，对应 prompts/characters/*.yaml 的文件名
            client_provider: API 提供商，默认 deepseek
            client_model: 模型名称，默认 deepseek-chat
        """
        self.char_id = char_id
        self.client = SimpleAPIClient(provider=client_provider, model=client_model)

        # 从 PromptManager 加载角色配置
        pm = get_prompt_manager()
        char_config = pm.get_character(char_id)

        self.name = char_config["name"]
        self.path = char_config["path"]
        self.drive = char_config["drive"]
        self.profile = char_config["profile"]
        # 精神状态 0-5，越高越正常
        self.state = 5
        # 黄金裔的记忆，初始值来自配置文件
        self.memory = list(char_config.get("memory", []))

    def answer(self, question):
        # 与黄金裔对话
        pm = get_prompt_manager()
        system_prompt = pm.get_system_prompt(self.char_id, memory=self.memory)
        response = self.client.chat(question, system_prompt)

        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(question, system_prompt)

        self.memory.append(response)
        return response

    def reflect(self):
        # 深思熟虑，会更新记忆，如果精神不正常就干不了了
        if self.state <= 1:
            return "精神状态过低，无法深思。"

        pm = get_prompt_manager()
        system_prompt = pm.get_system_prompt(self.char_id, memory=self.memory)
        question = pm.get_scene_prompt(
            "self_reflection",
            name=self.name,
            path=self.path,
            drive=self.drive,
            profile=self.profile,
            memory=self.memory,
        )
        response = self.client.chat(question, system_prompt)

        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(question, system_prompt)

        self.memory.append(response)
        return response

    def make_decision(self, question):
        # 做出决定，有固定返回格式
        if self.state == 0:
            return {"decision": "拒绝决策", "reason": "精神崩溃"}

        pm = get_prompt_manager()
        system_prompt = pm.get_system_prompt(self.char_id, memory=self.memory)
        decision_format = pm.get_decision_format()

        full_question = f"{question}\n\n{decision_format.format(name=self.name, path=self.path, drive=self.drive)}"
        response = self.client.chat(full_question, system_prompt)

        # 重试机制
        while response == '请求超时，请稍后重试':
            time.sleep(5)
            response = self.client.chat(full_question, system_prompt)

        self.memory.append(response)
        return response


'''

角色 ID 与中文名映射（从 PromptManager 动态生成）

'''

def _build_character_names():
    pm = get_prompt_manager()
    return pm.get_character_names()


CHARACTER_NAMES = _build_character_names()


'''

初始化黄金裔与盗火行者

'''


def init_chrysos_heir():
    """初始化所有黄金裔（不含盗火行者）"""
    pm = get_prompt_manager()
    heirs = {}
    for char_id in pm.get_all_character_ids():
        if char_id == "Black_NeiKo":
            continue
        heirs[char_id] = Chrysos_Heir(char_id=char_id)
    return heirs


def init_black_heir():
    """初始化盗火行者"""
    return {
        "Black_NeiKo": Chrysos_Heir(char_id="Black_NeiKo")
    }


if __name__ == "__main__":
    import itertools
    heirs = init_chrysos_heir()
    # for name, heir in itertools.islice(heirs.items(), 2):
    for name, heir in heirs.items():
        start_time = time.time()
        heir.reflect()
        res = heir.answer(question="你的愿望是？")
        end_time = time.time()
        print(f"{name}: {res}")
        print(f"时间：{end_time - start_time}秒")
        print('=====================')
