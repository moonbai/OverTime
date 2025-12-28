#!/bin/bash

echo "========================================"
echo "加班管理系统 - 依赖安装脚本"
echo "========================================"
echo ""

echo "[1/3] 检测Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.7+"
    exit 1
fi
PYTHON=$(command -v python3)
echo "✅ Python环境正常: $($PYTHON --version)"

echo ""
echo "[2/3] 安装必需依赖..."
echo "✅ 纯Python标准库实现，无需额外安装"

echo ""
echo "[3/3] 安装可选依赖（推荐）..."
echo ""

read -p "是否安装可选依赖（workalendar/openpyxl）？(y/n): " install_optionalif [[ "$install_optional" =~ ^[Yy]$ ]]; then
    echo "📦 正在安装workalendar（节假日判断增强）..."
    $PYTHON -m pip install workalendar --trusted-host pypi.org --trusted-host files.pythonhosted.org
    if [ $? -eq 0 ]; then
        echo "✅ workalendar安装成功"
    else
        echo "⚠️  workalendar安装失败，将使用内置节假日数据"
    fi

    echo ""
    echo "📦 正在安装openpyxl（Excel导出）..."
    $PYTHON -m pip install openpyxl --trusted-host pypi.org --trusted-host files.pythonhosted.org
    if [ $? -eq 0 ]; then
        echo "✅ openpyxl安装成功"
    else
        echo "⚠️  openpyxl安装失败，无法导出Excel"
    fi
else
    echo "⚠️  跳过可选依赖安装"
    echo "    - 节假日判断将使用内置数据（2024/2026年）"
    echo "    - 无法导出Excel文件"
fi

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "运行程序: $PYTHON main.py"
echo ""

# 赋予执行权限（如果需要）
chmod +x main.py 2>/dev/null || true
