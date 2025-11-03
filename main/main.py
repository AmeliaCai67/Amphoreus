# import stage
# import agent

def eternal_regression(rounds: int):
    import stage
    import agent
    """
    永劫回归测试函数
    
    模拟多轮迭代的永劫回归过程，每轮迭代中：
    1. 黄金裔根据神谕选择是否逐火
    2. 盗火行者劝说逐火者交出火种
    3. 顽固者经过多次劝说后仍不交出火种则被强夺
    4. 盗火行者收集所有火种并承载记忆
    5. 进入下一轮迭代，记忆不断累积
    
    Args:
        rounds (int): 迭代次数，决定永劫回归的轮数
    
    Returns:
        dict: 记录每轮迭代结果的日志字典
              格式: {'第X次永劫回归': (final_result, robbed_list)}
              - final_result: 该轮的火种收集结果字典
              - robbed_list: 该轮被强夺火种的角色列表
    
    Example:
        >>> logs = eternal_regression(rounds=6)
        >>> print(logs['第1次永劫回归'][0])  # 查看第1轮的火种收集结果
        >>> print(logs['第1次永劫回归'][1])  # 查看第1轮被强夺的角色
    """
    round_num = 0
    
    # 盗火行者可以跨迭代，记忆不断累积
    # 每轮迭代后，他们的记忆会包含之前所有轮次的信息
    black_heirs = agent.init_black_heir()
    
    # 总记录字典，用于追踪每轮迭代的完整结果
    logs_dict = {}

    print(f"=== 开始永劫回归测试，共 {rounds} 轮迭代 ===")
    print("=" * 60)

    # 主循环：执行指定轮数的永劫回归
    while round_num < rounds:
        round_num += 1
        print(f"\n🔄 第 {round_num} 轮永劫回归开始")
        print("-" * 40)
        
        # 执行一轮完整的迭代
        # 每轮迭代都会更新盗火行者的记忆
        final_result, robbed_list = stage.run_one_iteration(
            black_heirs=black_heirs, 
            max_persuasion_attempts=3
        )
        
        # 记录本轮迭代的结果
        logs_dict[f'第{round_num}次永劫回归'] = (final_result, robbed_list)
        
        # 显示本轮迭代的统计信息
        total_fire_chasers = len([s for s in final_result.values() if '逐火' in s])
        willing_handovers = len([s for s in final_result.values() if '交出火种' in s])
        forced_robberies = len([s for s in final_result.values() if '火种被强夺' in s])
        
        print(f"\n📊 第 {round_num} 轮统计:")
        print(f"   逐火者总数: {total_fire_chasers}")
        print(f"   主动交出火种: {willing_handovers}")
        print(f"   被强夺火种: {forced_robberies}")
        print(f"   不逐火者: {total_fire_chasers-willing_handovers-forced_robberies}")
        
        # 显示盗火行者的记忆累积情况
        for black_heir_name, black_heir in black_heirs.items():
            print(f"   {black_heir_name} 记忆条数: {len(black_heir.memory)}")
    
    print(f"\n🎯 永劫回归测试完成！共执行 {rounds} 轮迭代")
    print("=" * 60)
    
    return logs_dict

def analyze_regression_logs(logs_dict: dict):
    """
    分析永劫回归日志，提供统计洞察
    
    Args:
        logs_dict (dict): 永劫回归函数返回的日志字典
    
    Returns:
        dict: 分析结果
    """
    analysis = {
        '总轮数': len(logs_dict),
        '每轮统计': {},
        '趋势分析': {}
    }
    
    for round_key, (final_result, robbed_list) in logs_dict.items():
        round_num = round_key.replace('第', '').replace('次永劫回归', '')
        
        # 统计每轮的关键指标
        total_fire_chasers = len([s for s in final_result.values() if '逐火' in s])
        willing_handovers = len([s for s in final_result.values() if '交出火种' in s])
        forced_robberies = len([s for s in final_result.values() if '火种被强夺' in s])
        
        analysis['每轮统计'][round_num] = {
            '逐火者总数': total_fire_chasers,
            '主动交出火种': willing_handovers,
            '被强夺火种': forced_robberies,
            '不逐火者': total_fire_chasers-willing_handovers-forced_robberies,
            '被强夺角色': robbed_list
        }
    
    return analysis

def get_visualization_data(logs_dict):
    """将日志数据转换为可视化所需的格式"""
    visualization_data = []
    for round_key, (final_result, robbed_list) in logs_dict.items():
        round_data = {
            "round": round_key,
            "decisions": final_result,
            "robbed": robbed_list
        }
        visualization_data.append(round_data)
    return visualization_data
    
def eternal_regression_realtime_streaming(rounds: int):
    """
    永劫回归测试函数 - 实时流式版本（细粒度事件）
    
    使用生成器逐事件返回结果，每次角色说话都返回
    
    Args:
        rounds (int): 迭代次数
    
    Yields:
        dict: 事件字典，格式为 {'type': 'oracle'|'decision'|'persuasion'|'result', ...}
    """
    import stage
    import agent
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Starting eternal_regression_realtime_streaming with %s rounds", rounds)
    
    round_num = 0
    logger.info("Initializing black_heirs")
    black_heirs = agent.init_black_heir()
    logger.info("Initializing heirs")
    
    # 初始化黄金裔
    heirs = agent.init_chrysos_heir()
    logger.info("Heirs initialized, count = %s", len(heirs))
    
    logger.info("Yielding start event")
    yield {
        'type': 'start',
        'rounds': rounds
    }
    
    # 主循环
    while round_num < rounds:
        round_num += 1
        logger.info("Starting round %s", round_num)
        
        logger.info("Yielding round_start event")
        yield {
            'type': 'round_start',
            'round_num': round_num
        }
        
        # === 阶段1：神谕 ===
        logger.info("Getting oracle from HapLotes405")
        oracle = heirs['HapLotes405'].answer('尊贵的雅努萨布利斯的圣女，请怜悯大地上的众生，发布逐火的神谕吧！')
        logger.info("Got oracle, length = %s", len(oracle))
        
        logger.info("Yielding oracle event")
        yield {
            'type': 'oracle',
            'char_id': 'HapLotes405',
            'char_name': '缇宝',
            'message': oracle
        }
        
        # === 阶段2：众人逐火决策 ===
        logger.info("Starting fire decisions")
        for char_id, heir in heirs.items():
            logger.info("Getting decision from %s", char_id)
            res = heir.make_decision(question=f"是否逐火？神谕：{oracle}")
            
            # 解析决策
            logger.info("Decoding decision for %s", char_id)
            decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
            logger.info("Decision for %s: %s", char_id, decision)
            
            logger.info("Yielding fire_decision event for %s", char_id)
            yield {
                'type': 'fire_decision',
                'char_id': char_id,
                'char_name': agent.CHARACTER_NAMES.get(char_id, char_id) if hasattr(agent, 'CHARACTER_NAMES') else char_id,
                'decision': decision,
                'message': res
            }
        
        # 记录逐火结果
        fire_chasers_dict = {}
        for char_id, heir in heirs.items():
            decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
            if decision == '1':
                fire_chasers_dict[char_id] = '逐火'
            else:
                fire_chasers_dict[char_id] = '不逐火'
        
        yield {
            'type': 'fire_result',
            'result': fire_chasers_dict
        }
        
        # === 阶段3：盗火行者劝说 ===
        black_heir_word = ""
        for char_id, heir in black_heirs.items():
            black_heir_word = heir.answer(question="作为来自未来的救世主，请劝诫已然踏上逐火之旅的黄金裔，让他们把火种交给你吧。")
            yield {
                'type': 'persuasion',
                'char_id': char_id,
                'char_name': '盗火行者·白厄',
                'message': black_heir_word
            }
        
        # === 阶段4：是否交出火种 ===
        for char_id, heir in heirs.items():
            if fire_chasers_dict[char_id] == '逐火':
                res = heir.make_decision(question=f"是否将火种交给他？面前这个奇怪的黄金裔劝说道：{black_heir_word}")
                decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                
                yield {
                    'type': 'handover_decision',
                    'char_id': char_id,
                    'char_name': agent.CHARACTER_NAMES.get(char_id, char_id) if hasattr(agent, 'CHARACTER_NAMES') else char_id,
                    'decision': decision,
                    'message': res
                }
        
        # 更新结果
        for char_id, heir in heirs.items():
            if fire_chasers_dict[char_id] == '逐火':
                decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                if decision == '1':
                    fire_chasers_dict[char_id] += '_交出火种'
                else:
                    fire_chasers_dict[char_id] += '_不交出火种'
        
        yield {
            'type': 'handover_result',
            'result': fire_chasers_dict
        }
        
        # === 阶段5：劝说顽固者 ===
        robbed_characters = []
        for attempt in range(3):  # max_persuasion_attempts
            stubborn_fire_chasers = [name for name, status in fire_chasers_dict.items() 
                                    if status == '逐火_不交出火种']
            
            if not stubborn_fire_chasers:
                break
            
            yield {
                'type': 'persuasion_attempt',
                'attempt': attempt + 1,
                'targets': stubborn_fire_chasers
            }
            
            # 盗火行者劝说
            import random
            for char_id, heir in black_heirs.items():
                if stubborn_fire_chasers:
                    target_name = random.choice(stubborn_fire_chasers)
                    stubborn_fire_chasers.remove(target_name)
                    
                    res = heir.answer(question=f"继续劝说{target_name}交出火种，这是第{attempt + 1}次尝试。请用更有说服力的方式劝说。")
                    yield {
                        'type': 'persuasion_detail',
                        'persuader_id': char_id,
                        'persuader_name': '盗火行者·白厄',
                        'target_id': target_name,
                        'target_name': agent.CHARACTER_NAMES.get(target_name, target_name) if hasattr(agent, 'CHARACTER_NAMES') else target_name,
                        'message': res
                    }
            
            # 重新决策
            for char_id in [n for n, status in fire_chasers_dict.items() if status == '逐火_不交出火种']:
                heir = heirs[char_id]
                res = heir.make_decision(question=f"盗火行者再次劝说，这是第{attempt + 1}次。你是否改变主意，愿意交出火种？")
                decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                
                yield {
                    'type': 'handover_redecision',
                    'char_id': char_id,
                    'char_name': agent.CHARACTER_NAMES.get(char_id, char_id) if hasattr(agent, 'CHARACTER_NAMES') else char_id,
                    'decision': decision,
                    'message': res
                }
            
            # 更新状态
            for char_id, heir in heirs.items():
                if fire_chasers_dict[char_id] == '逐火_不交出火种':
                    decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                    if decision == '1':
                        fire_chasers_dict[char_id] = '逐火_交出火种'
        
        # === 阶段6：强夺火种 ===
        for char_id, status in fire_chasers_dict.items():
            if status == '逐火_不交出火种':
                fire_chasers_dict[char_id] = '逐火_火种被强夺'
                robbed_characters.append(char_id)
                yield {
                    'type': 'robbery',
                    'char_id': char_id,
                    'char_name': agent.CHARACTER_NAMES.get(char_id, char_id) if hasattr(agent, 'CHARACTER_NAMES') else char_id
                }
        
        # === 阶段7：承载记忆 ===
        for black_heir_id, black_heir in black_heirs.items():
            for char_id, status in fire_chasers_dict.items():
                if status in ['逐火_交出火种', '逐火_火种被强夺']:
                    for memory in heirs[char_id].memory:
                        black_heir.memory.append(memory)
                elif status == '不逐火':
                    if heirs[char_id].memory:
                        black_heir.memory.append(heirs[char_id].memory[0])
            
            black_heir.memory.append(f"被强夺火种的角色：{robbed_characters}，这些角色因被强夺火种受伤甚至死亡")
        
        yield {
            'type': 'round_end',
            'round_num': round_num,
            'final_result': fire_chasers_dict,
            'robbed_characters': robbed_characters,
            'memory_count': {bid: len(heir.memory) for bid, heir in black_heirs.items()}
        }
    
    yield {
        'type': 'complete',
        'total_rounds': rounds
    }


if __name__ == "__main__":
    # 执行6轮永劫回归测试
    print("🚀 启动永劫回归测试程序")
    logs_dict = eternal_regression(rounds=6)
    
    # 分析测试结果
    print("\n📈 开始分析测试结果...")
    analysis = analyze_regression_logs(logs_dict)
    
    print(f"\n📊 测试结果分析:")
    print(f"   总测试轮数: {analysis['总轮数']}")
    
    for round_num, stats in analysis['每轮统计'].items():
        print(f"\n   第 {round_num} 轮详细统计:")
        for key, value in stats.items():
            if key != '被强夺角色':
                print(f"     {key}: {value}")
            else:
                print(f"     {key}: {value if value else '无'}")
    
    print("\n✅ 永劫回归测试程序执行完成！")


