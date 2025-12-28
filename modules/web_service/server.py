# modules/web_service/server.py
import socketserver
import threading
from datetime import datetime
from typing import Callable

class WebServiceModule:
    """Web服务模块"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.server = None
        self.thread = None
        self.running = False
        self.callbacks = {}

    def register_callback(self, name: str, callback: Callable):
        """注册回调函数"""
        self.callbacks[name] = callback

    def start(self) -> tuple:
        """启动Web服务"""
        if self.running:
            return False, "服务已在运行"

        try:
            from .handlers import OvertimeWebHandler

            port = self.config_manager.get('web_port', 8080)

            handler = lambda *args: OvertimeWebHandler(*args, callbacks=self.callbacks)
            self.server = socketserver.TCPServer(("", port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()

            self.running = True
            from core.utils import get_local_ip
            ip = get_local_ip()
            url = f"http://{ip}:{port}"

            return True, url
        except Exception as e:
            return False, str(e)

    def stop(self) -> tuple:
        """停止Web服务"""
        if not self.running:
            return False, "服务未运行"

        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()

            self.server = None
            self.thread = None
            self.running = False

            return True, "服务已停止"

        except Exception as e:
            return False, str(e)

    def get_status(self) -> dict:
        """获取服务状态"""
        if self.running:
            from core.utils import get_local_ip
            ip = get_local_ip()
            port = self.config_manager.get('web_port', 8080)
            url = f"http://{ip}:{port}"
            return {'running': True, 'url': url, 'port': port}
        else:
            return {'running': False, 'url': '', 'port': self.config_manager.get('web_port', 8080)}
