# modules/webhook.py
import json
import urllib.request
import urllib.error
from typing import Dict, Any

class WebhookModule:
    """Webhook同步模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def send(self, data: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """发送Webhook请求"""
        if not self.config_manager.get('webhook.enabled', False):
            return {'status': 'disabled', 'message': 'Webhook未启用'}

        url = self.config_manager.get('webhook.url', '')
        if not url:
            return {'status': 'error', 'message': 'URL未配置'}

        # 构建消息内容 -包含提交方式
        submit_method = data.get('提交方式', '未知')
        content = f"""📅 加班记录提交成功

日期: {data.get('日期', 'N/A')}
用户: {data.get('用户', 'N/A')}
类型: {data.get('工作类型', 'N/A')}
工作时长: {data.get('工作时长', 'N/A')} 小时
请假类型: {data.get('请假类型', '无')}
请假时长: {data.get('请假时长', '无')}
提交时间: {data.get('提交时间', 'N/A')}
提交方式: {submit_method}
工资: {data.get('工资', '未计算')}"""

        payload_data = {
            "msg_type": "text",
            "content": {"text": content}
        }

        try:
            payload = json.dumps(payload_data, ensure_ascii=False).encode('utf-8')
            headers = {'Content-Type': 'application/json; charset=utf-8'}

            # 自定义头
            try:
                custom_headers = json.loads(self.config_manager.get('webhook.headers', '{}'))
                if isinstance(custom_headers, dict):
                    headers.update(custom_headers)
            except:
                pass

            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
            timeout = self.config_manager.get('webhook.timeout', 10)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return {'status': 'success', 'code': response.status, 'data': result, 'platform': '飞书'}

        except urllib.error.HTTPError as e:
            error_msg = f"HTTP错误 {e.code}: {e.reason}"
            retry = self.config_manager.get('webhook.retry', 3)
            if retry_count < retry:
                return self.send(data, retry_count + 1)
            return {'status': 'error', 'message': error_msg, 'platform': '飞书'}

        except urllib.error.URLError as e:
            error_msg = f"连接错误: {str(e.reason)}"
            retry = self.config_manager.get('webhook.retry', 3)
            if retry_count < retry:
                return self.send(data, retry_count + 1)
            return {'status': 'error', 'message': error_msg, 'platform': '飞书'}

        except Exception as e:
            error_msg = f"发送失败: {str(e)}"
            retry = self.config_manager.get('webhook.retry', 3)
            if retry_count < retry:
                return self.send(data, retry_count + 1)
            return {'status': 'error', 'message': error_msg, 'platform': '飞书'}

    def test(self) -> Dict[str, Any]:
        """测试Webhook连接"""
        test_data = {
            "日期": "2026-02-17",
            "用户": "测试用户",
            "工作类型": "节假日",
            "工作时长": "8",
            "请假类型": "无",
            "请假时长": "无",
            "提交时间": "2026-02-17 10:00:00",
            "工资": "1600元",
            "提交方式": "测试"
        }
        return self.send(test_data)
