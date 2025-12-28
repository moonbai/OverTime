
### 2. install.bat (Windows批处理)

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo 加班管理系统 - 依赖安装脚本
echo ========================================
echo.

echo [1/3] 检测Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/3] 安装必需依赖...
echo✅ 纯Python标准库实现，无需额外安装

echo.
echo [3/3] 安装可选依赖（推荐）...
echo.

set /p install_optional="是否安装可选依赖（workalendar/openpyxl）？(y/n): "
if /i "%install_optional%"=="y" (
    echo 📦正在安装workalendar（节假日判断增强）...
    python -m pip install workalendar --trusted-host pypi.org --trusted-host files.pythonhosted.org    if %errorlevel% neq 0 (
        echo ⚠️  workalendar安装失败，将使用内置节假日数据
    ) else (
        echo ✅ workalendar安装成功
    )

    echo.
    echo 📦 正在安装openpyxl（Excel导出）...
    python -m pip install openpyxl --trusted-host pypi.org --trusted-host files.pythonhosted.org
    if %errorlevel% neq 0 (
        echo ⚠️  openpyxl安装失败，无法导出Excel
    ) else (
        echo ✅ openpyxl安装成功
    )
) else (
    echo ⚠️  跳过可选依赖安装
    echo -节假日判断将使用内置数据（2024/2026年）
    echo     - 无法导出Excel文件
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 运行程序: python main.py
echo.
pause
