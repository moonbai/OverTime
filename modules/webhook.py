# modules/webhook.py
import requests
import json
import time
from typing import Dict, Any, List, Tuple


class WebhookModule:
    """Webhook推送模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.platform_configs = {
            'feishu': {
                'name': '飞书',
                'url_hint': 'https://open.feishu.cn/open-apis/bot/v2/hook/xxxx',
                'format': 'interactive'
            },
            'dingtalk': {
                'name': '钉钉',
                'url_hint': 'https://oapi.dingtalk.com/robot/send?access_token=xxxx',
                'format': 'markdown'
            },
            'wechat': {
                'name': '企业微信',
                'url_hint': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx',
                'format': 'text'
            },
            'lark': {
                'name': 'Lark',
                'url_hint': 'https://open.larksuite.com/open-apis/bot/v2/hook/xxxx',
                'format': 'interactive'
            },
            'slack': {
                'name': 'Slack',
                'url_hint': 'https://hooks.slack.com/services/XXXX/XXXX/XXXX',
                'format': 'json'
            },
            'custom': {
                'name': '自定义',
                'url_hint': '任意Webhook URL',
                'format': 'json'
            }
        }

    def get_supported_platforms(self) -> List[Tuple[str, str, str]]:
        """获取支持的平台列表"""
        return [
            ('feishu', '飞书 (Feishu)', '企业级协作平台'),
            ('dingtalk', '钉钉 (DingTalk)', '阿里云办公平台'),
            ('wechat', '企业微信 (WeChat Work)', '腾讯企业办公'),
            ('lark', 'Lark (飞书国际版)', '字节跳动国际版'),
            ('slack', 'Slack', '国际团队协作'),
            ('custom', '自定义 (Custom)', '任意Webhook服务')
        ]

    def send(self, data: Dict[str, Any]) -> bool:
        """发送Webhook"""
        webhook_config = self.config_manager.get('webhook', {})

        if not webhook_config.get('enabled', False):
            return False

        url = webhook_config.get('url', '')
        if not url:
            print("❌ Webhook URL未配置")
            return False

        platform = webhook_config.get('platform', 'feishu')
        timeout = webhook_config.get('timeout', 10)
        retry = webhook_config.get('retry', 3)
        sync_mode = webhook_config.get('sync_mode', 'sync')

        payload = self._format_payload(data, platform)

        if sync_mode == 'async':
            import threading
            thread = threading.Thread(
                target=self._send_with_retry,
                args=(url, payload, timeout, retry, platform),
                daemon=True
            )
            thread.start()
            return True
        else:
            return self._send_with_retry(url, payload, timeout, retry, platform)

    def _get_web_info(self) -> Tuple[str, str]:
        """获取Web服务信息"""
        try:
            from core.utils import get_local_ip
            ip = get_local_ip()
            port = self.config_manager.get('web_port', 8080)
            return f"{ip}:{port}", f"http://{ip}:{port}"
        except:
            return "localhost:8080", "http://localhost:8080"

    def _format_payload(self, data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """根据平台格式化数据"""
        ip_port, web_url = self._get_web_info()

        if platform == 'feishu' or platform == 'lark':
            return self._build_feishu_card(data, ip_port, web_url)
        elif platform == 'dingtalk':
            return self._build_dingtalk_markdown(data, ip_port, web_url)
        elif platform == 'wechat':
            return self._build_wechat_text(data, ip_port, web_url)
        elif platform == 'slack':
            return self._build_slack_blocks(data, ip_port, web_url)
        elif platform == 'custom':
            payload = data.copy()
            payload['web_service'] = web_url
            payload['ip_port'] = ip_port
            return payload
        else:
            return data

    def _build_feishu_card(
        self,
        data: Dict[str, Any],
        ip_port: str,
        web_url: str
    ) -> Dict[str, Any]:
        """构建飞书卡片消息（字段拆分）"""
        fields = self._extract_fields(data)
        field_elements = []

        for i in range(0, len(fields), 2):
            pair = fields[i:i+2]
            field_tags = []
            for field in pair:
                field_tags.append({
                    "tag": "meta",
                    "label": field['label'],
                    "value": field['value']
                })

            if len(pair) == 1:
                field_elements.append({
                    "tag": "column_set",
                    "flex_mode": "none",
                    "horizontal_spacing": "default",
                    "vertical_spacing": "default",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "stretch",
                            "vertical_spacing": "default",
                            "horizontal_align": "default",
                            "elements": [{"tag": "meta", "label": pair[0]['label'], "value": pair[0]['value']}]
                        },
                        {
                            "tag": "column",
                            "width": "stretch",
                            "vertical_spacing": "default",
                            "horizontal_align": "default",
                            "elements": [{"tag": "meta", "label": "", "value": ""}]
                        }
                    ]
                })
            else:
                field_elements.append({
                    "tag": "column_set",
                    "flex_mode": "none",
                    "horizontal_spacing": "default",
                    "vertical_spacing": "default",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "stretch",
                            "vertical_spacing": "default",
                            "horizontal_align": "default",
                            "elements": [{"tag": "meta", "label": pair[0]['label'], "value": pair[0]['value']}]
                        },
                        {
                            "tag": "column",
                            "width": "stretch",
                            "vertical_spacing": "default",
                            "horizontal_align": "default",
                            "elements": [{"tag": "meta", "label": pair[1]['label'], "value": pair[1]['value']}]
                        }
                    ]
                })

        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📝 加班记录通知**\n>提交方式: {data.get('提交方式', '未知')}"
                }
            },
            *field_elements,
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": f"📊 打开Web服务"
                        },
                        "url": web_url,
                        "type": "primary"
                    }
                ]
            }
        ]

        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📋 加班记录通知"
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }

    def _extract_fields(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """提取字段列表"""
        return [
            {"label": "📅 日期", "value": data.get('日期', '-')},
            {"label": "👤 用户", "value": data.get('用户', '-')},
            {"label": "📆 加班类型", "value": data.get('加班类型', '-')},
            {"label": "⏰ 加班时长", "value": f"{data.get('加班时长', '-')}小时"},
            {"label": "🏥 请假类型", "value": data.get('请假类型', '无')},
            {"label": "⏳ 请假时长", "value": f"{data.get('请假时长', '-')}小时"},
            {"label": "💰 加班工资", "value": data.get('加班工资', '0')},
            {"label": "🕐 提交时间", "value": data.get('提交时间', '-')},
        ]

    def _build_dingtalk_markdown(
        self,
        data: Dict[str, Any],
        ip_port: str,
        web_url: str
    ) -> Dict[str, Any]:
        """构建钉钉Markdown消息"""
        fields = self._extract_fields(data)

        content_lines = ["**📋 加班记录通知**\n"]
        for field in fields:
            content_lines.append(f"- **{field['label']}**: {field['value']}")

        content_lines.append(f"\n---\n[📊 打开Web服务]({web_url})")

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": "加班记录通知",
                "text": "\n".join(content_lines)
            }
        }

    def _build_wechat_text(
        self,
        data: Dict[str, Any],
        ip_port: str,
        web_url: str
    ) -> Dict[str, Any]:
        """构建企业微信文本消息"""
        fields = self._extract_fields(data)

        content_lines = ["📋 加班记录通知"]
        for field in fields:
            content_lines.append(f"{field['label']}: {field['value']}")

        content_lines.append(f"\n📊 Web服务: {web_url}")

        return {
            "msgtype": "text",
            "text": {
                "content": "\n".join(content_lines)
            }
        }

    def _build_slack_blocks(
        self,
        data: Dict[str, Any],
        ip_port: str,
        web_url: str
    ) -> Dict[str, Any]:
        """构建Slack Block Kit消息"""
        fields = self._extract_fields(data)

        section_fields = []
        for field in fields:
            section_fields.append({
                "type": "mrkdwn",
                "text": f"*{field['label']}*\n{field['value']}"
            })

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 加班记录通知",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": section_fields
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 打开Web服务",
                            "emoji": True
                        },
                        "url": web_url,
                        "style": "primary"
                    }
                ]
            }
        ]

        return {"blocks": blocks}

    def _send_with_retry(
        self,
        url: str,
        payload: Dict[str, Any],
        timeout: int,
        retry: int,
        platform: str
    ) -> bool:
        """带重试的发送"""
        platform_name = self.platform_configs.get(platform, {}).get('name', platform)

        for i in range(retry):
            try:
                headers = {'Content-Type': 'application/json'}

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )

                if response.status_code == 200:
                    print(f"✅ {platform_name} Webhook发送成功")
                    return True
                else:
                    print(f"⚠️ {platform_name} 返回错误: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"❌ {platform_name} 发送失败 (尝试 {i+1}/{retry}): {e}")
                if i < retry - 1:
                    time.sleep(1)

        return False

    def test(self) -> Dict[str, Any]:
        """测试Webhook连接"""
        webhook_config = self.config_manager.get('webhook', {})

        if not webhook_config.get('enabled', False):
            return {'status': 'error', 'message': 'Webhook未启用'}

        url = webhook_config.get('url', '')
        if not url:
            return {'status': 'error', 'message': 'URL未配置'}

        platform = webhook_config.get('platform', 'feishu')
        timeout = webhook_config.get('timeout', 10)

        test_data = {
            '日期': '2024-01-04',
            '用户': '测试用户',
            '加班类型': '调休日',
            '加班时长': '8',
            '请假类型': '无',
            '请假时长': '无',
            '加班工资': '400.00元',
            '提交时间': '2024-12-28 14:30:22',
            '提交方式': '测试推送'
        }

        payload = self._format_payload(test_data, platform)

        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)

            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': f'{self.platform_configs[platform]["name"]} 连接正常',
                    'code': response.status_code,
                    'platform': self.platform_configs[platform]["name"]
                }
            else:
                return {
                    'status': 'error',
                    'message': f'状态码: {response.status_code}, 响应: {response.text}',
                    'code': response.status_code
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_url_hint(self, platform: str) -> str:
        """获取平台URL提示"""
        return self.platform_configs.get(platform, {}).get('url_hint', '')

    def get_format_info(self, platform: str) -> str:
        """获取平台格式说明"""
        format_map = {
            'feishu': 'Interactive卡片（字段拆分）+ 按钮',
            'dingtalk': 'Markdown格式 + 链接，请设置**加班**为关键词',
            'wechat': 'Text文本（字段分行）',
            'lark': 'Interactive卡片（字段拆分）+ 按钮',
            'slack': 'Block Kit（字段分列）+ 按钮',
            'custom': '完整数据JSON'
        }
        return format_map.get(platform, '未知格式')
