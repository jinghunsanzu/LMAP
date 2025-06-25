"""安全分析服务层"""

from typing import Dict, Any, List
from .ai_service import ai_service
from ..utils import handle_service_error, LoggerMixin, Validator
from ..utils.exceptions import ValidationError, APIException


class AnalysisService(LoggerMixin):
    """安全分析服务"""
    
    def __init__(self):
        self.ai_service = ai_service
    
    @handle_service_error
    def analyze_traffic(self, http_data: str) -> Dict[str, Any]:
        """分析网络流量"""
        # 验证输入
        Validator.validate_http_data(http_data)
        
        self.logger.info(f"开始流量分析，数据长度: {len(http_data)}")
        
        # 构建流量分析提示模板
        base_prompt = """请进行网络安全分析。请严格按照以下步骤执行：
1. 分析以下HTTP请求的各个组成部分
2. 识别是否存在SQL注入、XSS、CSRF、反序列化、文件上传、路径遍历、OWASPTop10、等常见攻击特征
3. 检查User-Agent等头部信息是否可疑
4. 如果数据包中有一些编码后的内容，一定要解码后再进行分析
5. 最终结论：是否为攻击流量（是/否）

请用中文按以下格式响应：
【分析结果】是/否
【依据】简明扼要列出技术依据

HTTP请求数据：
{content}"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=http_data,
            temperature=0.3
        )
        is_attack = "【分析结果】是" in result
        
        self.logger.info(f"流量分析完成，检测结果: {'攻击' if is_attack else '正常'}")
        
        return {
            "result": result,
            "is_attack": is_attack,
            "analysis_type": "traffic_analysis"
        }
    
    @handle_service_error
    def decode_string(self, encoded_str: str) -> Dict[str, Any]:
        """智能解码字符串"""
        # 验证输入
        Validator.validate_required(encoded_str, "编码字符串")
        
        self.logger.info(f"开始字符串解码，长度: {len(encoded_str)}")
        
        # 构建解码提示模板
        base_prompt = """请完整分析并解码以下字符串，要求：
1. 识别所有可能的编码方式（包括嵌套编码）
2. 通过自己重新编码，确认自己解码正确
3. 展示完整的解码过程
4. 输出最终解码结果

原始字符串：{content}

请用中文按以下格式响应：
【编码分析】列出检测到的编码类型及层级
【解码过程】逐步展示解码步骤
【最终结果】解码后的明文内容"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=encoded_str,
            temperature=0.3
        )
        
        self.logger.info("字符串解码完成")
        
        return {
            "result": result,
            "analysis_type": "string_decode"
        }
    
    @handle_service_error
    def analyze_javascript(self, js_code: str) -> Dict[str, Any]:
        """JavaScript安全审计"""
        # 验证输入
        Validator.validate_js_code(js_code)
        
        self.logger.info(f"开始JavaScript审计，代码长度: {len(js_code)}")
        
        # 构建JavaScript审计提示模板
        base_prompt = """请对以下JavaScript代码进行完整的安全审计，要求：
1. 识别XSS、CSRF、不安全的DOM操作、敏感信息泄露、eval使用等安全问题
2. 检查第三方库的安全性和版本漏洞
3. 分析代码逻辑漏洞
4. 提供修复建议

请用中文按以下格式响应：
【高危漏洞】列出高危安全问题及位置
【中低危问题】列出中低风险问题
【修复建议】提供具体修复方案

JavaScript代码：
{content}"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=js_code,
            temperature=0.3
        )
        
        self.logger.info("JavaScript审计完成")
        
        return {
            "result": result,
            "analysis_type": "javascript_audit"
        }
    
    @handle_service_error
    def analyze_process(self, process_data: str) -> Dict[str, Any]:
        """进程分析"""
        # 验证输入
        Validator.validate_process_data(process_data)
        
        self.logger.info(f"开始进程分析，数据长度: {len(process_data)}")
        
        prompt = f"""你是一个Windows/Linux进程分析工程师，要求：
1. 用户将输出tasklist或者ps aux的结果
2. 帮助用户分析输出你所有认识的进程信息
3. 识别可能的恶意进程
4. 识别杀毒软件进程
5. 识别其他软件进程

tasklist或者ps aux的结果：{process_data}

按优先级列出需要关注的进程
【可疑进程】
【杀软进程】
【第三方软件进程】
给出具体操作建议：
• 安全进程的可终止性评估"""
        
        result = self.ai_service.chat_completion(prompt)
        
        self.logger.info("进程分析完成")
        
        return {
            "result": result,
            "analysis_type": "process_analysis"
        }
    
    @handle_service_error
    def generate_regex(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """生成正则表达式"""
        # 验证输入
        Validator.validate_required(source_text, "源文本")
        Validator.validate_required(target_text, "目标文本")
        
        self.logger.info(f"开始生成正则表达式，源文本长度: {len(source_text)}, 目标长度: {len(target_text)}")
        
        prompt = f"""请根据以下要求生成正则表达式：

源文本：
{source_text}

需要匹配的目标：
{target_text}

要求：
1. 生成能够准确匹配目标文本的正则表达式
2. 考虑边界情况和特殊字符
3. 提供多种匹配方案（严格匹配、宽松匹配等）
4. 解释正则表达式的含义
5. 提供测试用例

请用中文按以下格式响应：
【推荐正则】最佳匹配方案
【备选方案】其他可选的正则表达式
【表达式解释】详细说明正则含义
【测试用例】提供测试示例"""
        
        result = self.ai_service.chat_completion(prompt)
        
        self.logger.info("正则表达式生成完成")
        
        return {
            "result": result,
            "analysis_type": "regex_generation"
        }
    
    @handle_service_error
    def detect_webshell(self, file_content: str, file_name: str = "") -> Dict[str, Any]:
        """WebShell检测"""
        # 验证输入
        Validator.validate_file_content(file_content)
        
        self.logger.info(f"开始WebShell检测，文件: {file_name}, 内容长度: {len(file_content)}")
        
        # 构建WebShell检测提示模板
        base_prompt = f"""请对以下文件进行WebShell检测分析：

文件名：{file_name or '未知'}
文件内容：
{{content}}

要求：
1. 识别是否为WebShell
2. 分析WebShell类型和功能
3. 识别危险函数和恶意代码
4. 评估威胁等级
5. 提供处置建议

请用中文按以下格式响应：
【检测结果】是否为WebShell（是/否）
【威胁等级】高危/中危/低危/无威胁
【恶意特征】列出发现的恶意代码特征
【功能分析】分析WebShell的主要功能
【处置建议】提供具体的安全处置方案"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=file_content,
            temperature=0.3
        )
        is_webshell = "【检测结果】是" in result
        
        # 提取威胁等级
        threat_level = "未知"
        if "【威胁等级】高危" in result:
            threat_level = "高危"
        elif "【威胁等级】中危" in result:
            threat_level = "中危"
        elif "【威胁等级】低危" in result:
            threat_level = "低危"
        elif "【威胁等级】无威胁" in result:
            threat_level = "无威胁"
        
        self.logger.info(f"WebShell检测完成，结果: {'发现WebShell' if is_webshell else '未发现WebShell'}, 威胁等级: {threat_level}")
        
        return {
            "result": result,
            "is_webshell": is_webshell,
            "threat_level": threat_level,
            "file_name": file_name,
            "analysis_type": "webshell_detection"
        }
    
    @handle_service_error
    def analyze_web_logs(self, log_content: str, analysis_options: List[str]) -> Dict[str, Any]:
        """Web日志分析"""
        # 验证输入
        Validator.validate_file_content(log_content)
        
        if not analysis_options:
            analysis_options = ["攻击检测", "异常分析", "统计分析"]
        
        self.logger.info(f"开始Web日志分析，日志长度: {len(log_content)}, 分析选项: {analysis_options}")
        
        # 构建分析提示
        analysis_tasks = []
        if "攻击检测" in analysis_options:
            analysis_tasks.append("识别SQL注入、XSS、文件包含、命令执行等攻击行为")
        if "异常分析" in analysis_options:
            analysis_tasks.append("检测异常访问模式、可疑IP、异常User-Agent")
        if "统计分析" in analysis_options:
            analysis_tasks.append("统计访问频率、热门页面、错误代码分布")
        if "性能分析" in analysis_options:
            analysis_tasks.append("分析响应时间、资源消耗、性能瓶颈")
        
        # 构建基础提示模板
        base_prompt = f"""请对以下Web访问日志进行安全分析：

分析任务：
{chr(10).join(f'{i+1}. {task}' for i, task in enumerate(analysis_tasks))}

Web访问日志：
{{content}}

请用中文按以下格式响应：
【攻击检测】列出发现的攻击行为和威胁
【异常分析】识别异常访问模式和可疑活动
【统计分析】提供访问统计和趋势分析
【安全建议】提供具体的安全加固建议"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=log_content,
            temperature=0.3
        )
        
        self.logger.info("Web日志分析完成")
        
        return {
            "result": result,
            "analysis_options": analysis_options,
            "analysis_type": "web_log_analysis"
        }
    
    @handle_service_error
    def chat_weblog(self, question: str, log_content: str, analysis_result: Any) -> Dict[str, Any]:
        """Web日志对话"""
        try:
            # 详细的输入验证和日志记录
            self.logger.info(f"开始Web日志对话 - 问题: '{question[:50]}...', 日志长度: {len(log_content)}, 分析结果类型: {type(analysis_result)}")
            
            # 验证输入
            if not question or not question.strip():
                raise ValidationError("问题不能为空")
            
            if len(question) > 1000:
                raise ValidationError("问题长度不能超过1000字符")
                
            if not log_content or not log_content.strip():
                raise ValidationError("日志内容不能为空")
            
            Validator.validate_text_input(question, "问题", 1000)
            
            # 提取分析结果文本
            try:
                if isinstance(analysis_result, dict):
                    analysis_text = analysis_result.get('result', str(analysis_result))
                else:
                    analysis_text = str(analysis_result)
                
                self.logger.info(f"分析结果文本长度: {len(analysis_text)}")
                
            except Exception as e:
                self.logger.warning(f"处理分析结果时出错: {e}, 使用默认值")
                analysis_text = "暂无分析结果"
            
            # 构建对话提示模板
            base_prompt = f"""你是一个专业的网络安全分析师，正在协助用户分析Web访问日志。

之前的分析结果：
{analysis_text}

用户问题：{question}

原始日志内容：
{{content}}

请基于上述日志内容和分析结果，详细回答用户的问题。回答要求：
1. 准确引用日志中的具体信息
2. 结合安全专业知识进行解释
3. 提供实用的安全建议
4. 使用中文回答
5. 如果问题涉及具体的攻击行为，请详细说明攻击手法和防护措施
6. 如果无法从日志中找到相关信息，请明确说明"""
            
            self.logger.info(f"基础提示长度: {len(base_prompt)}")
            
            # 使用支持分块的方法处理长文本
            try:
                result = self.ai_service.chat_completion_with_chunking(
                    base_prompt=base_prompt,
                    content=log_content,
                    temperature=0.3
                )
                
                if not result or not result.strip():
                    self.logger.warning("AI返回空结果，使用默认回答")
                    result = "抱歉，无法分析您的问题。请检查日志格式是否正确，或尝试重新表述您的问题。"
                
                self.logger.info(f"Web日志对话完成，回答长度: {len(result)}")
                
            except Exception as e:
                self.logger.error(f"AI服务调用失败: {e}")
                # 提供降级回答
                result = f"抱歉，处理您的问题时遇到技术问题：{str(e)}。请稍后重试或联系管理员。"
            
            return {
                "result": result,
                "question": question,
                "analysis_type": "web_log_chat"
            }
            
        except ValidationError:
            # 重新抛出验证错误
            raise
        except Exception as e:
            self.logger.error(f"Web日志对话处理失败: {e}")
            raise APIException(f"对话处理失败: {str(e)}")
    
    @handle_service_error
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """AI翻译"""
        # 验证输入
        Validator.validate_required(text, "翻译文本")
        Validator.validate_required(source_lang, "源语言")
        Validator.validate_required(target_lang, "目标语言")
        
        self.logger.info(f"开始AI翻译，文本长度: {len(text)}, {source_lang} -> {target_lang}")
        
        # 构建翻译提示模板
        base_prompt = f"""请将以下文本从{source_lang}翻译成{target_lang}：

原文：
{{content}}

要求：
1. 保持原文的语义和语调
2. 确保翻译的准确性和流畅性
3. 如果是技术文档，保持专业术语的准确性
4. 如果包含代码或特殊格式，请保持不变

请直接提供翻译结果，不需要额外说明。"""
        
        # 使用支持分块的方法处理长文本
        result = self.ai_service.chat_completion_with_chunking(
            base_prompt=base_prompt,
            content=text,
            temperature=0.1
        )
        
        self.logger.info("AI翻译完成")
        
        return {
            "result": result,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "analysis_type": "translation"
        }


# 全局分析服务实例
analysis_service = AnalysisService()