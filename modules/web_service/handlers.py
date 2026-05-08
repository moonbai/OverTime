# modules/web_service/handlers.py
import http.server
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from urllib.parse import parse_qs, urlparse


class APIResponse:
    """API响应封装"""

    @staticmethod
    def success(data: Any = None, message: str = "成功") -> Dict[str, Any]:
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def error(message: str, code: int = 400) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }


class RequestValidator:
    """请求验证器"""

    @staticmethod
    def validate_submit_data(data: Dict[str, Any]) -> tuple:
        """验证提交数据

        Returns:
            Tuple[是否有效, 错误信息]
        """
        required_fields = ['date', 'user', 'day_type']
        for field in required_fields:
            if not data.get(field):
                return False, f"缺少必填字段: {field}"
        return True, ""

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class OvertimeWebHandler(http.server.SimpleHTTPRequestHandler):
    """Web服务请求处理器"""

    def __init__(self, *args, callbacks: Optional[Dict[str, Callable]] = None, **kwargs):
        self.callbacks = callbacks or {}
        self.validator = RequestValidator()
        self.api_response = APIResponse()
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        """处理GET请求"""
        parsed_path = urlparse(self.path)

        routes = {
            '/': self._handle_index,
            '/index.html': self._handle_index,
            '/api/data': self._handle_api_data,
            '/api/check_date': self._handle_api_check_date,
            '/status': self._handle_status,
        }

        handler = routes.get(parsed_path.path)
        if handler:
            handler(parsed_path)
        else:
            self._handle_not_found()

    def do_POST(self) -> None:
        """处理POST请求"""
        routes = {
            '/submit': self._handle_submit_form,
            '/api/submit': self._handle_api_submit,
        }

        handler = routes.get(self.path)
        if handler:
            handler()
        else:
            self._handle_not_found()

    def _handle_index(self, parsed_path) -> None:
        """处理首页请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        html_callback = self.callbacks.get('get_html')
        if html_callback:
            html = html_callback()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.wfile.write(b"<html><body>Web UI</body></html>")

    def _handle_api_data(self, parsed_path) -> None:
        """处理数据API请求"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        data_callback = self.callbacks.get('get_data')
        if data_callback:
            data = data_callback()
        else:
            data = []

        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _handle_api_check_date(self, parsed_path) -> None:
        """处理日期检查API请求"""
        date_str = self._get_query_param(parsed_path.query, 'date')

        if not date_str:
            self.send_json_response(self.api_response.error("未提供日期参数"), 400)
            return

        if not self.validator.validate_date_format(date_str):
            self.send_json_response(self.api_response.error("日期格式错误，应为 YYYY-MM-DD"), 400)
            return

        check_callback = self.callbacks.get('check_date')
        if not check_callback:
            self.send_json_response(self.api_response.error("回调未注册"), 500)
            return

        try:
            result = check_callback(date_str)
            if isinstance(result, tuple) and len(result) == 2:
                type_name, reason = result
                self.send_json_response({
                    'type': type_name,
                    'reason': reason,
                    'date': date_str
                })
            else:
                self.send_json_response(self.api_response.error("返回格式错误"), 500)
        except Exception as e:
            self.send_json_response(self.api_response.error(str(e)), 500)

    def _handle_status(self, parsed_path) -> None:
        """处理状态检查请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def _handle_submit_form(self) -> None:
        """处理表单提交"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_html(400, "请求体为空")
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)

            data = self._parse_form_data(params)

            is_valid, error_msg = self.validator.validate_submit_data(data)
            if not is_valid:
                self._send_error_html(400, error_msg)
                return

            result = self._execute_submit(data)
            self._send_submit_result(result)

        except Exception as e:
            self._send_error_html(500, f"服务器错误: {str(e)}")

    def _handle_api_submit(self) -> None:
        """处理API提交"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response(self.api_response.error("请求体为空"), 400)
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            data['submit_method'] = 'API'

            is_valid, error_msg = self.validator.validate_submit_data(data)
            if not is_valid:
                self.send_json_response(self.api_response.error(error_msg), 400)
                return

            result = self._execute_submit(data)
            self.send_json_response(result)

        except json.JSONDecodeError:
            self.send_json_response(self.api_response.error("JSON格式错误"), 400)
        except Exception as e:
            self.send_json_response(self.api_response.error(str(e)), 500)

    def _handle_not_found(self) -> None:
        """处理404请求"""
        self.send_error(404, "Page not found")

    def _get_query_param(self, query: str, key: str) -> Optional[str]:
        """从查询字符串获取参数"""
        if not query:
            return None
        params = parse_qs(query)
        values = params.get(key, [None])
        return values[0] if values else None

    def _parse_form_data(self, params: dict) -> Dict[str, Any]:
        """解析表单数据"""
        return {
            'date': self._get_param_first(params, 'date'),
            'user': self._get_param_first(params, 'user'),
            'day_type': self._get_param_first(params, 'day_type'),
            'is_leave': self._get_param_first(params, 'is_leave'),
            'leave_type': self._get_param_first(params, 'leave_type'),
            'leave_hours': self._get_param_first(params, 'leave_hours'),
            'work_hours': self._get_param_first(params, 'work_hours'),
            'submit_method': '网页填报'
        }

    def _get_param_first(self, params: dict, key: str) -> str:
        """获取参数的第一个值"""
        values = params.get(key, [''])
        return values[0] if values else ''

    def _execute_submit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行提交逻辑"""
        submit_callback = self.callbacks.get('submit_record')
        if not submit_callback:
            return self.api_response.error("提交功能未实现")

        try:
            success, message, record = submit_callback(data)
            return {
                'status': 'success' if success else 'error',
                'message': message,
                'record': record
            }
        except Exception as e:
            return self.api_response.error(str(e))

    def _send_submit_result(self, result: Dict[str, Any]) -> None:
        """发送提交结果HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        is_success = result.get('status') == 'success'
        title = "✓ 提交成功！" if is_success else "✗ 提交失败"
        color = "green" if is_success else "red"
        message = result.get('message', '')

        html = f"""
<html>
<head><meta charset="UTF-8"><title>提交结果</title></head>
<body style="font-family: Microsoft YaHei; padding: 20px;">
    <h2 style="color: {color};">{title}</h2>
    <p>{message}</p>
    <p><a href="/">返回填报页面</a></p>
</body>
</html>
"""
        self.wfile.write(html.encode('utf-8'))

    def _send_error_html(self, code: int, message: str) -> None:
        """发送错误HTML"""
        self.send_error(code, message)

    def send_json_response(self, data: Dict[str, Any], code: int = 200) -> None:
        """发送JSON响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args) -> None:
        """抑制日志输出"""
        pass
