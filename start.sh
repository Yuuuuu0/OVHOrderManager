#!/bin/bash

# 设置工作目录为脚本所在目录
# shellcheck disable=SC2164
cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "正在安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "错误：.env 文件不存在！"
    echo "请根据 .env.example 创建 .env 文件"
    exit 1
fi

# 启动程序
echo "启动OVH订单管理器..."
python main.py

# 如果程序异常退出，保持终端窗口打开
read -p "程序已退出，按回车键关闭窗口..."