# main.py
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"\n{'='*60}")
    print("程序崩溃！")
    print(f"{'='*60}")
    print(error_msg)

    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("程序崩溃",
            f"程序遇到严重错误，请截图保存以下信息：\n\n{error_msg[:800]}...")
    except:
        pass

    try:
        with open('error_log.txt', 'w', encoding='utf-8') as f:
            f.write(error_msg)
        print("\n错误日志已保存到: error_log.txt")
    except:
        pass

    sys.exit(1)

if __name__ == "__main__":
    sys.excepthook = handle_exception

    try:
        from system import OvertimeSystem

        root = tk.Tk()
        root.title("加班管理系统 - 模块化架构")
        root.geometry("850x900")

        system = OvertimeSystem(root)
        root.mainloop()

    except Exception as e:
        print(f"\n{'='*60}")
        print("启动失败！")
        print(f"{'='*60}")
        print(traceback.format_exc())
        input("\n按回车键退出...")
        sys.exit(1)
