# modules/web_service/handlers.py
import http.server
import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse

class OvertimeWebHandler(http.server.SimpleHTTPRequestHandler):
    """Web服务请求处理器"""

    def __init__(self, *args, callbacks=None, **kwargs):
        self.callbacks = callbacks or {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = self.callbacks.get('get_html', lambda: "<html><body>Web UI</body></html>")()
            self.wfile.write(html.encode('utf-8'))

        elif parsed_path.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = self.callbacks.get('get_data', lambda: [])()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        elif parsed_path.path == '/api/check_date':
            # 正确解析日期参数
            query = parsed_path.query
            date = None

            if query:
                #尝试两种格式：date=2024-01-01 或直接2024-01-01
                if 'date=' in query:
                    params = parse_qs(query)
                    date = params.get('date', [None])[0]
                else:
                    date = query

            if not date:
                self.send_json_response({'error': '未提供日期参数'}, 400)
                return

            if self.callbacks.get('check_date'):
                try:
                    result = self.callbacks['check_date'](date)
                    #确保返回格式正确
                    if isinstance(result, tuple) and len(result) == 2:
                        type_name, reason = result
                        self.send_json_response({
                            'type': type_name,
                            'reason': reason,
                            'date': date
                        })
                    else:
                        self.send_json_response({'error': '返回格式错误'}, 500)
                except Exception as e:
                    self.send_json_response({'error': str(e)}, 500)
            else:
                self.send_json_response({'error': '回调未注册'}, 500)

        elif parsed_path.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        if self.path == '/submit':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = parse_qs(post_data)

                data = {
                    'date': params.get('date', [''])[0],
                    'user': params.get('user', [''])[0],
                    'day_type': params.get('day_type', [''])[0],
                    'is_leave': params.get('is_leave', [''])[0],
                    'leave_type': params.get('leave_type', [''])[0],
                    'leave_hours': params.get('leave_hours', [''])[0],
                    'work_hours': params.get('work_hours', [''])[0],
                    'submit_method': '网页'
                }

                if not data['date'] or not data['user'] or not data['day_type']:
                    self.send_error(400, "缺少必填字段")
                    return

                # 处理提交
                result = self.callbacks.get('submit_record', lambda d: (False, "未实现", None))(data)

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                success, message, record = result
                if success:
                    html = f"""
<html>
<head><meta charset="UTF-8"><title>提交结果</title></head>
<body style="font-family: Microsoft YaHei; padding: 20px;">
    <h2 style="color: green;">✓ 提交成功！</h2>
    <p>{message}</p>
    <p><a href="/">返回填报页面</a></p>
</body>
</html>
"""
                else:
                    html = f"""
<html>
<head><meta charset="UTF-8"><title>提交失败</title></head>
<body style="font-family: Microsoft YaHei; padding: 20px;">
    <h2 style="color: red;">✗ 提交失败</h2>
    <p>{message}</p>
    <p><a href="/">返回重试</a></p>
</body>
</html>
"""
                self.wfile.write(html.encode('utf-8'))

            except Exception as e:
                self.send_error(500, f"服务器错误: {str(e)}")

        elif self.path == '/api/submit':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                data['submit_method'] = 'API'

                result = self.callbacks.get('submit_record', lambda d: (False, "未实现", None))(data)
                success, message, record = result

                response = {'status': 'success' if success else 'error', 'message': message}
                if record:
                    response['record'] = record

                self.send_json_response(response)

            except Exception as e:
                self.send_json_response({'status': 'error', 'message': str(e)}, 500)

        else:
            self.send_error(404, "Not found")

    def send_json_response(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        pass
