"""AI服务层"""

import requests
import json
import re
from typing import Optional, Dict, Any, List
from ..config import config_manager, APIConfig
from ..utils import (
    AIServiceError, AuthenticationError, RateLimitError, 
    handle_service_error, LoggerMixin
)


class AIService(LoggerMixin):
    """AI服务统一接口"""
    
    def __init__(self):
        self.config = config_manager.get_api_config()
        self.timeout = 120
    
    def reload_config(self) -> None:
        """重新加载配置"""
        config_manager.load_config()
        self.config = config_manager.get_api_config()
        self.logger.info(f"AI服务配置已重新加载: {self.config.api_type}")
    
    @handle_service_error
    def chat_completion(self, prompt: str, temperature: float = 0.3) -> str:
        """统一的聊天完成接口"""
        self.logger.info(f"开始AI请求: {self.config.api_type}, prompt长度: {len(prompt)}")
        
        # 验证配置
        errors = self.config.validate()
        if errors:
            raise AIServiceError(f"配置验证失败: {'; '.join(errors)}")
        
        try:
            if self.config.api_type == "deepseek":
                return self._call_deepseek(prompt, temperature)
            elif self.config.api_type == "openrouter":
                return self._call_openrouter(prompt, temperature)
            elif self.config.api_type == "ollama":
                return self._call_ollama(prompt, temperature)
            else:
                raise AIServiceError(f"不支持的API类型: {self.config.api_type}")
        except Exception as e:
            self.logger.error(f"AI请求失败: {str(e)}")
            raise
    
    def _call_deepseek(self, prompt: str, temperature: float) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            return self._handle_response(response, "DeepSeek")
            
        except requests.exceptions.Timeout:
            raise AIServiceError("DeepSeek API请求超时")
        except requests.exceptions.ConnectionError:
            raise AIServiceError("无法连接到DeepSeek API")
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"DeepSeek API请求失败: {str(e)}")
    
    def _call_openrouter(self, prompt: str, temperature: float) -> str:
        """调用OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # 可选，用于统计
            "X-Title": "DeepSeek Security Analysis Platform"  # 可选，用于统计
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            return self._handle_response(response, "OpenRouter")
            
        except requests.exceptions.Timeout:
            raise AIServiceError("OpenRouter API请求超时")
        except requests.exceptions.ConnectionError:
            raise AIServiceError("无法连接到OpenRouter API")
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"OpenRouter API请求失败: {str(e)}")
    
    def _call_ollama(self, prompt: str, temperature: float) -> str:
        """调用Ollama API"""
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                self.config.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise AIServiceError(f"Ollama API返回错误状态码: {response.status_code}")
            
            try:
                response_data = response.json()
                if "message" not in response_data or "content" not in response_data["message"]:
                    raise AIServiceError("Ollama API响应格式错误")
                
                content = response_data["message"]["content"]
                # 移除思考标签
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                return content.strip()
                
            except json.JSONDecodeError:
                raise AIServiceError("Ollama API响应不是有效的JSON格式")
            
        except requests.exceptions.Timeout:
            raise AIServiceError("Ollama API请求超时")
        except requests.exceptions.ConnectionError:
            raise AIServiceError("无法连接到Ollama服务")
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"Ollama API请求失败: {str(e)}")
    
    def _handle_response(self, response: requests.Response, api_name: str) -> str:
        """处理API响应"""
        # 检查状态码
        if response.status_code == 401:
            raise AuthenticationError(f"{api_name} API认证失败，请检查API密钥")
        elif response.status_code == 429:
            raise RateLimitError(f"{api_name} API请求频率超限，请稍后重试")
        elif response.status_code != 200:
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', {}).get('message', '未知错误')
            except:
                error_msg = response.text
            raise AIServiceError(f"{api_name} API返回错误状态码 {response.status_code}: {error_msg}")
        
        # 解析响应
        try:
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                raise AIServiceError(f"{api_name} API响应格式错误：缺少choices字段")
            
            choice = response_data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise AIServiceError(f"{api_name} API响应格式错误：缺少message.content字段")
            
            content = choice["message"]["content"]
            if not content:
                raise AIServiceError(f"{api_name} API返回空内容")
            
            return content
            
        except json.JSONDecodeError:
            raise AIServiceError(f"{api_name} API响应不是有效的JSON格式")
        except KeyError as e:
            raise AIServiceError(f"{api_name} API响应格式错误: 缺少字段 {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        test_prompt = "Hello, this is a test message. Please respond with 'Connection successful'."
        
        try:
            start_time = requests.utils.default_headers()
            response = self.chat_completion(test_prompt, temperature=0.1)
            
            return {
                "success": True,
                "message": "连接测试成功",
                "api_type": self.config.api_type,
                "model": self.config.model,
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}",
                "api_type": self.config.api_type,
                "model": self.config.model
            }
    
    def get_api_info(self) -> Dict[str, Any]:
        """获取当前API信息"""
        return {
            "api_type": self.config.api_type,
            "api_url": self.config.api_url,
            "model": self.config.model,
            "has_api_key": bool(self.config.api_key and self.config.api_key.strip())
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量（更保守的估算）"""
        # 对于中文文本，1个token约等于1.5-2个字符
        # 对于英文文本，1个token约等于4个字符
        # 为了安全起见，使用更保守的估算
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        
        # 中文字符按1.5个字符=1个token计算，其他字符按3个字符=1个token计算
        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 3)
        return estimated_tokens
    
    def _get_max_tokens(self) -> int:
        """获取当前模型的最大token限制"""
        # 根据不同模型设置不同的token限制
        model_limits = {
            "deepseek-chat": 65536,
            "deepseek-coder": 65536,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 4096,
            "claude-3": 200000,
        }
        
        # 默认使用65536，为安全起见留出更多余量
        max_tokens = model_limits.get(self.config.model, 65536)
        return int(max_tokens * 0.6)  # 留出40%的余量给系统提示和响应，更加保守
    
    def _split_text_by_lines(self, text: str, max_tokens: int) -> List[str]:
        """按行分割文本，确保每个块不超过token限制"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self._estimate_tokens(line)
            
            # 如果单行就超过限制，需要进一步分割
            if line_tokens > max_tokens:
                # 先保存当前块
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # 分割长行
                char_limit = max_tokens * 4  # 粗略估算字符数
                for i in range(0, len(line), char_limit):
                    chunks.append(line[i:i + char_limit])
                continue
            
            # 检查是否会超过限制
            if current_tokens + line_tokens > max_tokens:
                # 保存当前块并开始新块
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                # 添加到当前块
                current_chunk.append(line)
                current_tokens += line_tokens
        
        # 添加最后一个块
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def chat_completion_with_chunking(self, base_prompt: str, content: str, 
                                    temperature: float = 0.3, 
                                    chunk_prompt_template: str = None) -> str:
        """支持文本分块的聊天完成接口"""
        # 估算总token数
        total_tokens = self._estimate_tokens(base_prompt + content)
        max_tokens = self._get_max_tokens()
        
        self.logger.info(f"文本分块处理 - 内容长度: {len(content)}, 估算token数: {total_tokens}, 最大限制: {max_tokens}")
        
        # 如果不超过限制，直接调用原方法
        if total_tokens <= max_tokens:
            full_prompt = base_prompt.replace("{content}", content)
            return self.chat_completion(full_prompt, temperature)
        
        # 需要分块处理
        self.logger.info("内容过长，开始分块处理")
        
        # 计算可用于内容的token数
        base_tokens = self._estimate_tokens(base_prompt)
        # 留出更多缓冲：基础提示 + 分块说明 + 响应空间
        buffer_tokens = 2000  # 增加缓冲区
        available_tokens = max_tokens - base_tokens - buffer_tokens
        
        if available_tokens <= 0:
            raise AIServiceError("基础提示过长，无法进行分块处理")
        
        # 分割内容
        chunks = self._split_text_by_lines(content, available_tokens)
        self.logger.info(f"内容已分割为 {len(chunks)} 个块，可用token数: {available_tokens}")
        
        # 记录每个块的大小
        for i, chunk in enumerate(chunks, 1):
            chunk_tokens = self._estimate_tokens(chunk)
            self.logger.info(f"第{i}块: {len(chunk)}字符, 估算{chunk_tokens}个token")
        
        # 设置分块提示模板
        if chunk_prompt_template is None:
            chunk_prompt_template = base_prompt + "\n\n注意：这是第{chunk_index}/{total_chunks}部分内容，请分析这部分内容：\n{content}"
        
        # 处理每个块
        results = []
        for i, chunk in enumerate(chunks, 1):
            # 先替换base_prompt中的{content}占位符
            current_prompt = base_prompt.replace("{content}", chunk)
            # 如果使用自定义模板，则格式化模板
            if chunk_prompt_template != base_prompt + "\n\n注意：这是第{chunk_index}/{total_chunks}部分内容，请分析这部分内容：\n{content}":
                chunk_prompt = chunk_prompt_template.format(
                    chunk_index=i,
                    total_chunks=len(chunks),
                    content=chunk
                )
            else:
                chunk_prompt = current_prompt + f"\n\n注意：这是第{i}/{len(chunks)}部分内容。"
            
            self.logger.info(f"处理第 {i}/{len(chunks)} 个块")
            try:
                result = self.chat_completion(chunk_prompt, temperature)
                results.append(f"=== 第{i}部分分析结果 ===\n{result}")
            except Exception as e:
                self.logger.error(f"处理第 {i} 个块时出错: {str(e)}")
                results.append(f"=== 第{i}部分分析失败 ===\n错误: {str(e)}")
        
        # 合并结果
        combined_result = "\n\n".join(results)
        
        # 如果合并后的结果仍然很长，可以进行总结
        if len(results) > 3:  # 如果有超过3个块，生成总结
            summary_prompt = f"""请对以下分块分析结果进行总结和汇总：

{combined_result}

请提供一个综合性的分析总结，包括：
1. 主要发现和威胁
2. 整体安全状况评估
3. 关键建议和处置方案"""
            
            try:
                summary = self.chat_completion(summary_prompt, temperature)
                return f"{combined_result}\n\n=== 综合分析总结 ===\n{summary}"
            except Exception as e:
                self.logger.error(f"生成总结时出错: {str(e)}")
                return combined_result
        
        return combined_result


# 全局AI服务实例
ai_service = AIService()