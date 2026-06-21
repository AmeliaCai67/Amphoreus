import agent
import json
import time

# API 设定
from config.api_config import SimpleAPIClient
from prompt_manager import get_prompt_manager


def decode_decision_from_memory(name: str, last_memory):
    """
    从记忆中解析决策结果，尝试三次：1) 正则匹配 2) json.loads 3) ast.literal_eval，均失败则报告失败。

    返回:
        '1' 表示同意，'0' 表示拒绝，'' 表示解析失败
    """

    import re, json, ast, time

    def _normalize_decision(val):
        if isinstance(val, bool):
            return '1' if val else '0'
        if isinstance(val, int):
            return '1' if val == 1 else '0' if val == 0 else ''
        if isinstance(val, str):
            s = val.strip()
            return '1' if s == '1' else '0' if s == '0' else ''
        return ''

    def _extract_from_dict(d):
        if not isinstance(d, dict):
            return ''
        # 优先查找常见键名
        for k in ('decision', 'Decision', "'decision'"):
            if k in d:
                return _normalize_decision(d[k])
        # 兼容字符串键
        if 'decision' in d:
            return _normalize_decision(d['decision'])
        return ''

    # 如果已经是 dict-like，直接解析
    if not isinstance(last_memory, str):
        res = _extract_from_dict(last_memory)
        if res:
            return res
        print(f"{name or '未知角色'}的最后一条记忆解析失败")
        return ''

    # 如果是字符串，尝试三次（每次按顺序使用三种方法）
    for attempt in range(3):
        # 1) 正则匹配，支持单/双引号
        match = re.search(r"""['"]?decision['"]?\s*:\s*['"]?([01])['"]?""", last_memory)
        if match:
            return match.group(1)

        # 2) 尝试用 json.loads 解析
        try:
            obj = json.loads(last_memory)
            res = _extract_from_dict(obj)
            if res:
                return res
        except Exception:
            pass

        # 3) 尝试用 ast.literal_eval 解析（安全的 python literal 解析）
        try:
            obj = ast.literal_eval(last_memory)
            res = _extract_from_dict(obj)
            if res:
                return res
        except Exception:
            pass

        # 小间隔后重试
        time.sleep(0.1)

    # 三次尝试均失败, 调用ai模型解析
    pm = get_prompt_manager()
    api_client = SimpleAPIClient(provider="deepseek", model="deepseek-chat")
    prompt = pm.get_decode_fallback_prompt(text=last_memory)
    response = api_client.chat(content=prompt, system_prompt="你是一个专业的文本解析助手。")
    res = _normalize_decision(response)
    if res:
        return res
    else:
        print(f"{name or '未知角色'}的最后一条记忆解析失败")
        return ''


def run_one_iteration(black_heirs: dict, max_persuasion_attempts=5):
    """
    运行一轮完整的迭代

    Args:
        black_heirs(dict):盗火行者
        max_persuasion_attempts (int): 最大劝说次数，默认5次

    Returns:
        dict: 最终的火种收集结果
        list: 被强夺火种的角色列表
    """
    iteration_start_time = time.time()
    pm = get_prompt_manager()

    print(f"=== 开始新一轮迭代（最大劝说次数：{max_persuasion_attempts}）===")
    print('=' * 60)

    '''
    =================================

    缇宝：传播神谕

    =================================

    '''
    heirs = agent.init_chrysos_heir()
    start_time = time.time()
    oracle_question = pm.get_scene_prompt("oracle")
    oracle = heirs['HapLotes405'].answer(oracle_question)
    print(f'神谕：{oracle}')
    end_time = time.time()
    print(f"发布神谕时间：{end_time - start_time}秒")
    print('=====================')

    '''
    =================================

    众人：选择是否逐火

    =================================

    '''

    for name, heir in heirs.items():
        # 缇宝是神谕发布者，天然逐火，不参与决策
        if name == 'HapLotes405':
            continue

        start_time = time.time()
        question = pm.get_scene_prompt(
            "fire_decision",
            name=heir.name,
            path=heir.path,
            drive=heir.drive,
            profile=heir.profile,
            memory=heir.memory,
            oracle=oracle,
        )
        res = heir.make_decision(question=question)
        end_time = time.time()
        print(f"{name}: {res}")
        print(f"决策时间：{end_time - start_time}秒")
        print('=====================')

    # 记录逐火结果
    fire_chasers_dict = {}
    for name, heir in heirs.items():
        if name == 'HapLotes405':
            fire_chasers_dict[name] = '逐火'
            continue

        # 获取最后一条记忆并解析JSON
        last_memory = heir.memory[-1]
        # print(f"解析{name}的最后一条记忆：{last_memory}\n类型: {type(last_memory)}")
        decision = decode_decision_from_memory(name, last_memory)

        if decision == '1':
            fire_chasers_dict[name] = '逐火'
        elif decision == '0':
            fire_chasers_dict[name] = '不逐火'
        else:
            fire_chasers_dict[name] = '不逐火'  # 默认不逐火

    print(f"逐火结果：{fire_chasers_dict}")
    print('=====================')

    '''
    =================================

    盗火行者：劝诫黄金裔交出火种

    =================================

    '''

    black_heirs_word = ""
    for name, heir in black_heirs.items():
        start_time = time.time()
        question = pm.get_scene_prompt("black_heir_persuade")
        black_heirs_word = heir.answer(question=question)
        end_time = time.time()
        print(f"{name}: {black_heirs_word}")
        print(f"耗时：{end_time - start_time}秒")
        print('=====================')

    '''
    =================================

    黄金裔：是否交出火种

    =================================

    '''

    # 缇宝作为神谕发布者，确保记忆中有逐火决策，以便参与交火种决策
    tribbie_fire_memory = json.dumps({
        'decision': '1',
        'reason': '我是神谕的传递者，自然响应逐火之路。'
    }, ensure_ascii=False)
    heirs['HapLotes405'].memory.append(tribbie_fire_memory)

    for name, heir in heirs.items():
        if fire_chasers_dict[name] == '逐火':
            start_time = time.time()
            question = pm.get_scene_prompt(
                "handover_decision",
                name=heir.name,
                path=heir.path,
                drive=heir.drive,
                profile=heir.profile,
                memory=heir.memory,
                black_heir_word=black_heirs_word,
            )
            res = heir.make_decision(question=question)
            end_time = time.time()
            print(f"{name}: {res}")
            print(f"决策时间：{end_time - start_time}秒")
            print('=====================')

    # 记录结果
    for name, heir in heirs.items():
        if fire_chasers_dict[name] == '逐火':
            # 获取最后一条记忆并解析JSON
            last_memory = heir.memory[-1]
            decision = decode_decision_from_memory(name, last_memory)

            if decision == '1':
                fire_chasers_dict[name] += '_交出火种'
            elif decision == '0':
                fire_chasers_dict[name] += '_不交出火种'
            else:
                fire_chasers_dict[name] += '_不交出火种'  # 默认不交出火种

    print(f"收集火种结果：{fire_chasers_dict}")
    print('=====================')

    '''
    =================================

    盗火行者：劝说逐火但不愿意交出火种的黄金裔

    =================================

    '''

    # 记录被强夺火种的角色
    robbed_characters = []

    for attempt in range(max_persuasion_attempts):
        print(f"\n=== 第 {attempt + 1} 次劝说 ===")

        # 找出当前仍不愿意交出火种的逐火者
        stubborn_fire_chasers = [name for name, status in fire_chasers_dict.items()
                                if status == '逐火_不交出火种']

        if not stubborn_fire_chasers:
            print("所有逐火者都已交出火种，无需继续劝说")
            break

        print(f"当前仍不交出火种的逐火者：{stubborn_fire_chasers}")

        # 盗火行者分别劝说
        for name, heir in black_heirs.items():
            if stubborn_fire_chasers:
                # 随机选择一个顽固的逐火者进行劝说
                import random
                target_name = random.choice(stubborn_fire_chasers)
                stubborn_fire_chasers.remove(target_name)  # 从列表中移除，避免重复劝说

                start_time = time.time()
                question = pm.get_scene_prompt(
                    "persuade_target",
                    target_name=target_name,
                    attempt=attempt + 1,
                )
                res = heir.answer(question=question)
                end_time = time.time()
                print(f"{name} 劝说 {target_name}: {res}")
                print(f"耗时：{end_time - start_time}秒")
                print('=====================')

        # 让顽固的逐火者重新决策
        for name in [n for n, status in fire_chasers_dict.items() if status == '逐火_不交出火种']:
            heir = heirs[name]
            start_time = time.time()
            question = pm.get_scene_prompt(
                "reconsider",
                name=heir.name,
                path=heir.path,
                drive=heir.drive,
                profile=heir.profile,
                memory=heir.memory,
                attempt=attempt + 1,
            )
            res = heir.make_decision(question=question)
            end_time = time.time()
            print(f"{name}: {res}")
            print(f"决策时间：{end_time - start_time}秒")
            print('=====================')

        # 更新决策结果
        for name, heir in heirs.items():
            if fire_chasers_dict[name] == '逐火_不交出火种':
                # 获取最后一条记忆并解析JSON
                last_memory = heir.memory[-1]
                decision = decode_decision_from_memory(name, last_memory)

                if decision == '1':
                    fire_chasers_dict[name] = '逐火_交出火种'
                    print(f"{name} 在第 {attempt + 1} 次劝说后改变主意，交出火种")
                elif decision == '0':
                    fire_chasers_dict[name] = '逐火_不交出火种'
                    print(f"{name} 在第 {attempt + 1} 次劝说后仍坚持不交出火种")
                else:
                    fire_chasers_dict[name] = '逐火_不交出火种'
                    print(f"{name} 在第 {attempt + 1} 次劝说后未做出决策")

    # 强夺火种
    print("\n=== 强夺火种阶段 ===")
    for name, status in fire_chasers_dict.items():
        if status == '逐火_不交出火种':
            print(f"盗火行者强夺 {name} 的火种")
            fire_chasers_dict[name] = '逐火_火种被强夺'
            robbed_characters.append(name)

    print(f"\n最终结果：{fire_chasers_dict}")
    print(f"被强夺火种的角色：{robbed_characters}")
    print('=====================')

    '''
    =================================

    盗火行者：承载所有的火种，进入下一轮迭代

    =================================

    '''

    # 盗火行者收集所有火种并写入记忆
    for black_heir_name, black_heir in black_heirs.items():
        print(f"\n=== {black_heir_name} 收集火种 ===")

        # 收集逐火者的记忆
        for name, status in fire_chasers_dict.items():
            if status in ['逐火_交出火种', '逐火_火种被强夺']:
                # 写入逐火者的所有记忆
                print(f"收集 {name} 的所有记忆（{len(heirs[name].memory)}条）")
                for memory in heirs[name].memory:
                    black_heir.memory.append(memory)
            elif status == '不逐火':
                # 仅写入第一条记忆
                if heirs[name].memory:
                    print(f"收集 {name} 的第一条记忆")
                    black_heir.memory.append(heirs[name].memory[0])

        # 写入被强夺记忆的角色
        black_heir.memory.append(f"被强夺火种的角色：{robbed_characters}，这些角色因被强夺火种受伤甚至死亡")

        # 打印盗火行者的所有记忆
        print(f"\n{black_heir_name} 的记忆内容：")
        print("=" * 50)

        total_chars = 0
        for i, memory in enumerate(black_heir.memory):
            memory_str = str(memory)
            chars_count = len(memory_str)
            total_chars += chars_count

        print(f"\n{black_heir_name} 总记忆条数: {len(black_heir.memory)}")
        print(f"{black_heir_name} 总字符数: {total_chars}")
        print("=" * 50)

    print("\n=== 火种收集完成 ===")
    print("所有盗火行者已承载火种，准备进入下一轮迭代")

    # 计算并显示本轮迭代总时间
    iteration_end_time = time.time()
    total_iteration_time = iteration_end_time - iteration_start_time
    print(f"本轮迭代总耗时：{total_iteration_time:.2f}秒")
    print('=' * 60)

    return fire_chasers_dict, robbed_characters


# 运行一轮迭代（可以调整劝说次数）
if __name__ == "__main__":
    black_heirs = agent.init_black_heir()
    final_result, robbed_list = run_one_iteration(black_heirs=black_heirs, max_persuasion_attempts=3)
