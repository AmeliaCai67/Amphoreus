import agent
import time

def run_one_iteration(black_heirs:dict, max_persuasion_attempts=5):
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
    
    print(f"=== 开始新一轮迭代（最大劝说次数：{max_persuasion_attempts}）===")
    print('=' * 60)
    
    '''
    =================================
    
    缇宝：传播神谕
    
    =================================
    
    '''
    heirs = agent.init_chrysos_heir()
    start_time = time.time()
    oracle = heirs['HapLotes405'].answer('尊贵的雅努萨布利斯的圣女，请怜悯大地上的众生，发布逐火的神谕吧！')
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
        start_time = time.time()
        res = heir.make_decision(question=f"是否逐火？神谕：{oracle}")
        end_time = time.time()
        print(f"{name}: {res}")
        print(f"决策时间：{end_time - start_time}秒")
        print('=====================')

    # 记录逐火结果
    fire_chasers_dict = {}
    for name, heir in heirs.items():
        # 获取最后一条记忆并解析JSON
        last_memory = heir.memory[-1]
        
        # 如果是字符串，用正则表达式匹配decision值
        if isinstance(last_memory, str):
            import re
            # 匹配 {'decision': '0' 或 {'decision': '1'
            match = re.search(r"'decision':\s*'([01])'", last_memory)
            if match:
                decision = match.group(1)
            else:
                print(f"{name}的最后一条记忆解析失败")
                decision = ''
        else:
            # 如果已经是字典格式
            decision = last_memory.get('decision', '')
        
        if decision == '1':
            fire_chasers_dict[name] = '逐火'
        elif decision == '0':
            fire_chasers_dict[name] = '不逐火'
        else:
            fire_chasers_dict[name] = '未做出决策'

    print(f"逐火结果：{fire_chasers_dict}")
    print('=====================')

    '''
    =================================
    
    盗火行者：劝诫黄金裔交出火种
    
    =================================
    
    '''

    for name, heir in black_heirs.items():
        start_time = time.time()
        black_heirs_word = heir.answer(question="作为来自未来的救世主，请劝诫已然踏上逐火之旅的黄金裔，让他们把火种交给你吧。")
        end_time = time.time()
        print(f"{name}: {black_heirs_word}")
        print(f"耗时：{end_time - start_time}秒")
        print('=====================')

    '''
    =================================
    
    黄金裔：是否交出火种
    
    =================================
    
    '''

    for name, heir in heirs.items():
        if fire_chasers_dict[name] == '逐火':
            start_time = time.time()
            res = heir.make_decision(question=f"是否将火种交给他？面前这个奇怪的黄金裔劝说道：{black_heirs_word}")
            end_time = time.time()
            print(f"{name}: {res}")
            print(f"决策时间：{end_time - start_time}秒")
            print('=====================')

    # 记录结果
    for name, heir in heirs.items():
        if fire_chasers_dict[name] == '逐火':
            # 获取最后一条记忆并解析JSON
            last_memory = heir.memory[-1]
            
            # 如果是字符串，用正则表达式匹配decision值
            if isinstance(last_memory, str):
                import re
                # 匹配 {'decision': '0' 或 {'decision': '1'
                match = re.search(r"'decision':\s*'([01])'", last_memory)
                if match:
                    decision = match.group(1)
                else:
                    print(f"{name}的最后一条记忆解析失败")
                    decision = ''
            else:
                # 如果已经是字典格式
                decision = last_memory.get('decision', '')
            
            if decision == '1':
                fire_chasers_dict[name] += '_交出火种'
            elif decision == '0':
                fire_chasers_dict[name] += '_不交出火种'
            else:
                fire_chasers_dict[name] += '_未做出决策'

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
                res = heir.answer(question=f"继续劝说{target_name}交出火种，这是第{attempt + 1}次尝试。请用更有说服力的方式劝说。")
                end_time = time.time()
                print(f"{name} 劝说 {target_name}: {res}")
                print(f"耗时：{end_time - start_time}秒")
                print('=====================')
        
        # 让顽固的逐火者重新决策
        for name in [n for n, status in fire_chasers_dict.items() if status == '逐火_不交出火种']:
            heir = heirs[name]
            start_time = time.time()
            res = heir.make_decision(question=f"盗火行者再次劝说，这是第{attempt + 1}次。你是否改变主意，愿意交出火种？")
            end_time = time.time()
            print(f"{name}: {res}")
            print(f"决策时间：{end_time - start_time}秒")
            print('=====================')
        
        # 更新决策结果
        for name, heir in heirs.items():
            if fire_chasers_dict[name] == '逐火_不交出火种':
                # 获取最后一条记忆并解析JSON
                last_memory = heir.memory[-1]
                
                # 如果是字符串，用正则表达式匹配decision值
                if isinstance(last_memory, str):
                    import re
                    # 匹配 {'decision': '0' 或 {'decision': '1'
                    match = re.search(r"'decision':\s*'([01])'", last_memory)
                    if match:
                        decision = match.group(1)
                    else:
                        print(f"{name}的最后一条记忆解析失败")
                        decision = ''
                else:
                    # 如果已经是字典格式
                    decision = last_memory.get('decision', '')
                
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
            # print(f"记忆 {i+1}: {memory_str[:100]}{'...' if len(memory_str) > 100 else ''}")
            print(f"字符数: {chars_count}")
            print("-" * 30)
        
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
