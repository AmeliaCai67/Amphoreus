import sys
import json
import traceback

try:
    import main

    def export_data(rounds=6):
        try:
            # 运行永劫回归模拟
            logs_dict = main.eternal_regression(rounds=rounds)
            
            # 转换为可视化数据
            rounds_data = main.get_visualization_data(logs_dict)
            
            # 构建符合C++端期望的数据格式
            visualization_data = {
                "global_logs": {
                    "start_message": f"=== 开始永劫回归测试，共 {len(logs_dict)} 轮迭代 ===",
                    "end_message": f"🎯 永劫回归测试完成！共执行 {len(logs_dict)} 轮迭代"
                },
                "rounds": rounds_data
            }
            
            # 输出JSON数据
            print(json.dumps(visualization_data, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"错误: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return False

    if __name__ == "__main__":
        # 获取命令行参数
        rounds = 6
        if len(sys.argv) > 1:
            try:
                rounds = int(sys.argv[1])
            except ValueError:
                print(f"错误: 无效的轮次参数 '{sys.argv[1]}'", file=sys.stderr)
                sys.exit(1)
        
        success = export_data(rounds)
        if not success:
            sys.exit(2)

except ImportError as e:
    print(f"导入错误: {str(e)}", file=sys.stderr)
    print("请确保在正确的目录中运行此脚本", file=sys.stderr)
    sys.exit(3)
except Exception as e:
    print(f"未预期的错误: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(4)