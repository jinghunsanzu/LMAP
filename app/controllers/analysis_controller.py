"""分析功能控制器"""

from flask import Blueprint, request, jsonify
from ..services import analysis_service
from ..utils import handle_api_error, ErrorHandler, Validator

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analyze_traffic', methods=['POST'])
@handle_api_error
def analyze_traffic():
    """流量分析接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    http_data = data.get('http_data', '')
    if not http_data:
        return ErrorHandler.format_validation_errors(["HTTP数据不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {"data_length": len(http_data)})
    
    result = analysis_service.analyze_traffic(http_data)
    return jsonify(result)


@analysis_bp.route('/decode', methods=['POST'])
@handle_api_error
def decode():
    """智能解码接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    encoded_str = data.get('encoded_str', '')
    if not encoded_str:
        return ErrorHandler.format_validation_errors(["编码字符串不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {"string_length": len(encoded_str)})
    
    result = analysis_service.decode_string(encoded_str)
    return jsonify(result)


@analysis_bp.route('/audit_js', methods=['POST'])
@handle_api_error
def audit_js():
    """JavaScript审计接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    js_code = data.get('js_code', '')
    if not js_code:
        return ErrorHandler.format_validation_errors(["JavaScript代码不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {"code_length": len(js_code)})
    
    result = analysis_service.analyze_javascript(js_code)
    return jsonify(result)


@analysis_bp.route('/analyze_process', methods=['POST'])
@handle_api_error
def analyze_process():
    """进程分析接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    process_data = data.get('process_data', '')
    if not process_data:
        return ErrorHandler.format_validation_errors(["进程数据不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {"data_length": len(process_data)})
    
    result = analysis_service.analyze_process(process_data)
    return jsonify(result)


@analysis_bp.route('/generate_regex', methods=['POST'])
@handle_api_error
def generate_regex():
    """正则表达式生成接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    source_text = data.get('source_text', '')
    target_text = data.get('target_text', '')
    
    if not source_text:
        return ErrorHandler.format_validation_errors(["源文本不能为空"]), 400
    if not target_text:
        return ErrorHandler.format_validation_errors(["目标文本不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {
        "source_length": len(source_text),
        "target_length": len(target_text)
    })
    
    result = analysis_service.generate_regex(source_text, target_text)
    return jsonify(result)


@analysis_bp.route('/detect_webshell', methods=['POST'])
@handle_api_error
def detect_webshell():
    """WebShell检测接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    file_content = data.get('file_content', '')
    file_name = data.get('file_name', '')
    
    if not file_content:
        return ErrorHandler.format_validation_errors(["文件内容不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {
        "file_name": file_name,
        "content_length": len(file_content)
    })
    
    result = analysis_service.detect_webshell(file_content, file_name)
    return jsonify(result)


@analysis_bp.route('/analyze_weblog', methods=['POST'])
@handle_api_error
def analyze_web_logs():
    """Web日志分析接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    log_content = data.get('log_content', '')
    analysis_options = data.get('analysis_types', [])
    
    if not log_content:
        return ErrorHandler.format_validation_errors(["日志内容不能为空"]), 400
    
    # 验证分析选项
    valid_options = ["攻击检测", "异常行为", "访问统计", "性能分析"]
    if analysis_options:
        invalid_options = [opt for opt in analysis_options if opt not in valid_options]
        if invalid_options:
            return ErrorHandler.format_validation_errors([
                f"无效的分析选项: {', '.join(invalid_options)}"
            ]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {
        "log_length": len(log_content),
        "analysis_options": analysis_options
    })
    
    result = analysis_service.analyze_web_logs(log_content, analysis_options)
    return jsonify(result)


@analysis_bp.route('/chat_weblog', methods=['POST'])
@handle_api_error
def chat_weblog():
    """Web日志对话接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    question = data.get('question', '')
    log_content = data.get('log_content', '')
    analysis_result = data.get('analysis_result', '')
    
    if not question:
        return ErrorHandler.format_validation_errors(["问题不能为空"]), 400
    
    if not log_content:
        return ErrorHandler.format_validation_errors(["日志内容不能为空"]), 400
    
    if not analysis_result:
        return ErrorHandler.format_validation_errors(["分析结果不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {
        "question_length": len(question),
        "log_length": len(log_content)
    })
    
    result = analysis_service.chat_weblog(question, log_content, analysis_result)
    return jsonify(result)


@analysis_bp.route('/translate', methods=['POST'])
@handle_api_error
def translate():
    """AI翻译接口"""
    data = request.get_json()
    if not data:
        return ErrorHandler.format_validation_errors(["请求数据不能为空"]), 400
    
    text = data.get('text', '')
    source_lang = data.get('source_lang', '')
    target_lang = data.get('target_lang', '')
    
    if not text:
        return ErrorHandler.format_validation_errors(["翻译文本不能为空"]), 400
    if not source_lang:
        return ErrorHandler.format_validation_errors(["源语言不能为空"]), 400
    if not target_lang:
        return ErrorHandler.format_validation_errors(["目标语言不能为空"]), 400
    
    # 记录请求信息
    ErrorHandler.log_request_info(request, {
        "text_length": len(text),
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    
    result = analysis_service.translate_text(text, source_lang, target_lang)
    return jsonify(result)