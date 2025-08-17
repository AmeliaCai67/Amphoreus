import requests
import json
import os
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv
import time

# 加载项目根目录下的.env文件
load_dotenv(override=True)

class SimpleAPIClient:
    """
    简化的API客户端，支持intern、deepseek、minimax
    支持模型名称和API key作为参数传入
    """
    
    def __init__(self, provider: str, api_key: str = None, model: str = None):
        """
        初始化API客户端
        Args:
            provider: API提供商 ("intern", "deepseek", "minimax")
            api_key: API密钥，如果不提供则从环境变量获取
            model: 模型名称，如果不提供则使用默认模型
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key_from_env()
        self.model = model
        self.response_time = 0  # 记录响应时间
        
        # 验证提供商
        if self.provider not in ["intern", "deepseek", "minimax"]:
            raise ValueError("provider必须是 'intern', 'deepseek' 或 'minimax' 之一")
        
        # 验证API密钥
        if not self.api_key:
            raise ValueError(f"未提供{self.provider}的API密钥，请检查环境变量或直接传入")
        
        # 设置默认模型和基础URL
        self._setup_provider_config()
    
    def _get_api_key_from_env(self) -> str:
        """从环境变量获取API密钥"""
        env_key_map = {
            "intern": "INTERN_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY", 
            "minimax": "MINIMAX_API_KEY"
        }
        return os.getenv(env_key_map.get(self.provider, ""))
        
    def _setup_provider_config(self):
        """设置提供商特定的配置"""
        if self.provider == "intern":
            self.base_url = os.getenv("INTERN_BASE_URL", "https://chat.intern-ai.org.cn/api/v1")
            self.default_model = os.getenv("INTERN_MODEL", "internlm3-latest")
        elif self.provider == "deepseek":
            self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            self.default_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        elif self.provider == "minimax":
            self.base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
            self.default_model = os.getenv("MINIMAX_MODEL", "MiniMax-M1")
        
        # 如果没有指定模型，使用默认模型
        if not self.model:
            self.model = self.default_model
    
    def get_headers(self):
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, 
             content: str, 
             system_prompt: str = None,
             temperature: float = 0.7,
             max_tokens: int = 1000,
             stream: bool = False) -> str:
        """
        发送聊天请求
        Args:
            content: 用户消息内容
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式响应
        Returns:
            str: 模型回复
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示词（如果提供）
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加用户消息
        messages.append({"role": "user", "content": content})
        
        # 准备请求体
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # 提供商特定的参数调整
        if self.provider == "minimax":
            # Minimax可能需要不同的参数格式
            if system_prompt:
                body["messages"] = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ]
        
        # 开始计时
        start_time = time.time()
        
        try:
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.get_headers(),
                json=body,
                timeout=60
            )
            
            # 计算响应时间
            self.response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"API调用失败 (HTTP {response.status_code})"
                try:
                    error_detail = response.json().get('error', {}).get('message', '')
                    if error_detail:
                        error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                return error_msg
                
        except requests.exceptions.Timeout:
            self.response_time = time.time() - start_time
            return "请求超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            self.response_time = time.time() - start_time
            return f"网络请求错误: {str(e)}"
        except Exception as e:
            self.response_time = time.time() - start_time
            return f"发生未知错误: {str(e)}"
    
    def get_response_time(self) -> float:
        """获取最后一次请求的响应时间（秒）"""
        return self.response_time
    
    def chat_stream(self, 
                   content: str, 
                   system_prompt: str = None,
                   temperature: float = 0.7,
                   max_tokens: int = 1000):
        """
        流式聊天请求
        Args:
            content: 用户消息内容
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
        Yields:
            str: 流式响应片段
        """
        # 构建消息列表
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": content})
        
        # 准备请求体
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        # 开始计时
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.get_headers(),
                json=body,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]  # 移除 'data: ' 前缀
                            if data == '[DONE]':
                                # 计算总响应时间
                                self.response_time = time.time() - start_time
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                self.response_time = time.time() - start_time
                yield f"API调用失败 (HTTP {response.status_code}): {response.text}"
                
        except Exception as e:
            self.response_time = time.time() - start_time
            yield f"流式请求错误: {str(e)}"


class APIManager:
    """
    API管理器，支持多个API提供商的统一管理
    """
    
    def __init__(self):
        self.clients = {}
        self.response_times = {}  # 记录每个客户端的响应时间
    
    def add_client(self, name: str, provider: str, api_key: str = None, model: str = None):
        """
        添加API客户端
        Args:
            name: 客户端名称
            provider: API提供商
            api_key: API密钥，如果不提供则从环境变量获取
            model: 模型名称
        """
        self.clients[name] = SimpleAPIClient(provider, api_key, model)
    
    def chat(self, client_name: str, content: str, **kwargs) -> str:
        """
        使用指定的客户端发送聊天请求
        Args:
            client_name: 客户端名称
            content: 消息内容
            **kwargs: 其他参数
        Returns:
            str: 模型回复
        """
        if client_name not in self.clients:
            raise ValueError(f"客户端 '{client_name}' 不存在")
        
        response = self.clients[client_name].chat(content, **kwargs)
        # 记录响应时间
        self.response_times[client_name] = self.clients[client_name].get_response_time()
        return response
    
    def chat_stream(self, client_name: str, content: str, **kwargs):
        """
        使用指定的客户端发送流式聊天请求
        Args:
            client_name: 客户端名称
            content: 消息内容
            **kwargs: 其他参数
        Yields:
            str: 流式响应片段
        """
        if client_name not in self.clients:
            raise ValueError(f"客户端 '{client_name}' 不存在")
        
        yield from self.clients[client_name].chat_stream(content, **kwargs)
        # 记录响应时间
        self.response_times[client_name] = self.clients[client_name].get_response_time()
    
    def get_response_time(self, client_name: str) -> float:
        """获取指定客户端的响应时间"""
        return self.response_times.get(client_name, 0.0)
    
    def get_all_response_times(self) -> Dict[str, float]:
        """获取所有客户端的响应时间"""
        return self.response_times.copy()
    
    def print_response_times(self):
        """打印所有客户端的响应时间"""
        print("\n=== 响应时间统计 ===")
        for client_name, response_time in self.response_times.items():
            print(f"{client_name}: {response_time:.2f}秒")
        print("=" * 30)


# 便捷函数
def create_client(provider: str, api_key: str = None, model: str = None) -> SimpleAPIClient:
    """
    创建API客户端的便捷函数
    Args:
        provider: API提供商
        api_key: API密钥，如果不提供则从环境变量获取
        model: 模型名称
    Returns:
        SimpleAPIClient: API客户端实例
    """
    return SimpleAPIClient(provider, api_key, model)


def chat_with_provider(provider: str, content: str, api_key: str = None, model: str = None, **kwargs) -> tuple:
    """
    直接与指定提供商聊天的便捷函数
    Args:
        provider: API提供商
        content: 消息内容
        api_key: API密钥，如果不提供则从环境变量获取
        model: 模型名称
        **kwargs: 其他参数
    Returns:
        tuple: (模型回复, 响应时间)
    """
    client = SimpleAPIClient(provider, api_key, model)
    response = client.chat(content, **kwargs)
    return response, client.get_response_time()


# 测试函数
def test_all_providers():
    """测试所有API提供商"""
    test_message = "你好，请简单介绍一下你自己"
    
    providers = [
        ("intern", "internlm3-latest"),
        ("deepseek", "deepseek-chat"),
        ("minimax", "MiniMax-M1")
    ]
    
    results = {}
    
    for provider, model in providers:
        print(f"\n=== 测试 {provider.upper()} API ===")
        try:
            response, response_time = chat_with_provider(provider, test_message, model=model)
            results[provider] = {
                "response": response,
                "time": response_time
            }
            print(f"回复: {response}")
            print(f"响应时间: {response_time:.2f}秒")
        except Exception as e:
            print(f"错误: {str(e)}")
            results[provider] = {
                "response": f"错误: {str(e)}",
                "time": 0.0
            }
        print("-" * 50)
    
    # 打印响应时间对比
    print("\n=== 响应时间对比 ===")
    for provider, result in results.items():
        print(f"{provider}: {result['time']:.2f}秒")
    
    return results


if __name__ == "__main__":
    # 示例用法
    print("=== API配置测试 ===")
    
    # # 方法1: 使用便捷函数（从环境变量获取API密钥）
    # print("\n1. 使用便捷函数（从环境变量获取API密钥）:")
    # try:
    #     response, response_time = chat_with_provider(
    #         provider="deepseek",
    #         content="你好，请介绍一下你自己",
    #         model="deepseek-chat"
    #     )
    #     print(f"DeepSeek回复: {response}")
    #     print(f"响应时间: {response_time:.2f}秒")
    # except Exception as e:
    #     print(f"错误: {str(e)}")
    
    # # 方法2: 使用SimpleAPIClient类（从环境变量获取API密钥）
    # print("\n2. 使用SimpleAPIClient类（从环境变量获取API密钥）:")
    # try:
    #     client = SimpleAPIClient(provider="intern", model="internlm3-latest")
    #     response = client.chat("你好，请介绍一下你自己")
    #     print(f"Intern回复: {response}")
    #     print(f"响应时间: {client.get_response_time():.2f}秒")
    # except Exception as e:
    #     print(f"错误: {str(e)}")
    
    # 方法3: 使用APIManager管理多个客户端（从环境变量获取API密钥）
    print("\n3. 使用APIManager（从环境变量获取API密钥）:")
    try:
        manager = APIManager()
        
        # 从环境变量获取API密钥
        # manager.add_client("intern", "intern", model="internlm3-latest")
        # manager.add_client("deepseek", "deepseek", model="deepseek-chat")
        manager.add_client("minimax", "minimax", model="MiniMax-M1")
        
        # 测试消息
        test_message = "你好，请简单介绍一下你自己"
        
        print(f"发送测试消息: {test_message}")
        
        # response1 = manager.chat("intern", test_message)
        # response2 = manager.chat("deepseek", test_message)
        response3 = manager.chat("minimax", test_message)
        
        # print(f"\nIntern回复: {response1}")
        # print(f"DeepSeek回复: {response2}")
        print(f"Minimax回复: {response3}")
        
        # 打印响应时间统计
        manager.print_response_times()

    except Exception as e:
        print(f"错误: {str(e)}")
    
    # # 运行所有提供商测试
    # print("\n=== 运行所有提供商测试 ===")
    # test_all_providers()