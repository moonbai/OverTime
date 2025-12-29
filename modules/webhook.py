# modules/webhook.py
import requests
import json
import time
from typing import Dict, Any, List, Tuple

class WebhookModule:
    """Webhook推送模块"""
    def __init__(self, config_manager):
        self.config_manager = config_manager

        # 平台配置映射
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

        # 根据平台格式化数据
        payload = self._format_payload(data, platform)

        # 同步或异步发送
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

    def _format_payload(self, data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """根据平台格式化数据"""

        # 获取IP:端口信息
        try:
            from core.utils import get_local_ip
            ip = get_local_ip()
            port = self.config_manager.get('web_port', 8080)
            ip_port = f"{ip}:{port}"
            web_url = f"http://{ip_port}"
        except:
            ip_port = "localhost:8080"
            web_url = "http://localhost:8080"

        if platform == 'feishu' or platform == 'lark':
            # 飞书/Lark - 卡片消息（按钮样式 + IP:端口）
            return {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "📝 加班记录通知"
                        },
                        "color": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "plain_text",
                                "content": self._build_text_content(data)
                            }
                        },
                        {
                            "tag": "action",
                            "actions": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": f"📊 Web服务: {ip_port}"
                                    },
                                    "url": web_url,
                                    "type": "default"
                                }
                            ]
                        }
                    ]
                }
            }

        elif platform == 'dingtalk':
            # 钉钉 - Markdown（链接样式）
            return {
                "msgtype": "markdown",
                "markdown": {
                    "title": "加班记录通知",
                    "text": self._build_markdown_content(data) + f"\n\n[🔗 **Web服务** - {ip_port}]({web_url})"
                }
            }

        elif platform == 'wechat':
            # 企业微信 - 文本消息 + IP:端口
            return {
                "msgtype": "text",
                "text": {
                    "content": self._build_text_content(data) + f"\n\n📊 Web服务: {web_url}\n📍 {ip_port}"
                }
            }

        elif platform == 'slack':
            # Slack - Block + 按钮
            return {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📝 加班记录通知"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": self._build_slack_content(data)
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": f"📊 Web服务: {ip_port}"
                                },
                                "url": web_url,
                                "style": "primary"
                            }
                        ]
                    }
                ]
            }

        elif platform == 'custom':
            # 自定义 - 完整数据 + Web服务地址
            payload = data.copy()
            payload['web_service'] = web_url
            payload['ip_port'] = ip_port
            return payload

        else:
            # 默认格式
            return data

    def _build_text_content(self, data: Dict[str, Any]) -> str:
        """构建文本内容"""
        return f"""加班记录通知
━━━━━━━━━━━━━━━━━━
日期: {data.get('日期', '')}
用户: {data.get('用户', '')}
加班类型: {data.get('加班类型', '')}
加班时长: {data.get('加班时长', '')}小时
请假类型: {data.get('请假类型', '无')}
请假时长: {data.get('请假时长', '无')}
加班工资: {data.get('加班工资', '0')}
提交时间: {data.get('提交时间', '')}
提交方式: {data.get('提交方式', '')}"""

    def _build_markdown_content(self, data: Dict[str, Any]) -> str:
        """构建Markdown内容"""
        return f"""**📝 加班记录通知**

>日期: **{data.get('日期', '')}**
> 用户: **{data.get('用户', '')}**
- 加班类型: {data.get('加班类型', '')}
- 加班时长: {data.get('加班时长', '')}小时
- 请假类型: {data.get('请假类型', '无')} ({data.get('请假时长', '无')})
- 加班工资: **{data.get('加班工资', '0')}**
- 提交时间: {data.get('提交时间', '')}
- 提交方式: {data.get('提交方式', '')}"""

    def _build_slack_content(self, data: Dict[str, Any]) -> str:
        """构建Slack内容"""
        return f"""*📝 加班记录通知*
• *日期*: {data.get('日期', '')}
• *用户*: {data.get('用户', '')}
• *加班类型*: {data.get('加班类型', '')}
• *加班时长*: {data.get('加班时长', '')}小时
• *请假类型*: {data.get('请假类型', '无')} ({data.get('请假时长', '无')})
• *加班工资*: *{data.get('加班工资', '0')}*
• *提交时间*: {data.get('提交时间', '')}
• *提交方式*: {data.get('提交方式', '')}"""

    def _send_with_retry(self, url: str, payload: Dict[str, Any], timeout: int, retry: int, platform: str) -> bool:
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

        # 测试数据
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
            'feishu': 'Interactive卡片 + 按钮(含IP:端口)',
            'dingtalk': 'Markdown格式 + 链接，因钉钉自定义机器人配置安全设置，请设置**加班**为关键词',
            'wechat': 'Text文本 + IP:端口',
            'lark': 'Interactive卡片 + 按钮',
            'slack': 'Block JSON + 按钮',
            'custom': '完整数据JSON + IP:端口'
        }
        return format_map.get(platform, '未知格式')
