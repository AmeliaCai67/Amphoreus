import stage
import agent

def eternal_regression(rounds: int):
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
    
    # # 存储全局日志信息
    # global_logs = {
    #     "start_message": f"=== 开始永劫回归测试，共 {len(logs_dict)} 轮迭代 ===",
    #     "end_message": f"🎯 永劫回归测试完成！共执行 {len(logs_dict)} 轮迭代"
    # }
    
    # # 处理每轮迭代的数据
    # for round_key, (final_result, robbed_list) in logs_dict.items():
    #     # 提取轮次编号
    #     round_num = round_key.replace('第', '').replace('次永劫回归', '')
        
    #     # 计算统计数据
    #     total_fire_chasers = len([s for s in final_result.values() if '逐火' in s])
    #     willing_handovers = len([s for s in final_result.values() if '交出火种' in s])
    #     forced_robberies = len([s for s in final_result.values() if '火种被强夺' in s])
    #     non_fire_chasers = total_fire_chasers - willing_handovers - forced_robberies
        
    #     # 构建本轮日志数据
    #     round_logs = {
    #         "start": f"🔄 第 {round_num} 轮永劫回归开始",
    #         "stats": {
    #             "逐火者总数": total_fire_chasers,
    #             "主动交出火种": willing_handovers,
    #             "被强夺火种": forced_robberies,
    #             "不逐火者": non_fire_chasers
    #         },
    #         "decisions": final_result,  # 各角色的决策结果
    #         "robbed": robbed_list      # 被强夺火种的角色列表
    #     }
        
    #     # 构建完整的轮次数据
    #     round_data = {
    #         "round": round_key,
    #         "round_num": int(round_num),
    #         "logs": round_logs
    #     }
        
    #     visualization_data.append(round_data)
    
    # # 按轮次排序
    # visualization_data.sort(key=lambda x: x["round_num"])
    
    # return {
    #     "global_logs": global_logs,
    #     "rounds": visualization_data
    # }
    
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


