#!/bin/bash

# 设置虚拟环境路径
VENV_DIR="venv"

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo ".env 文件不存在，请复制.env.example设置你要抢购的相关信息，并保存为.env文件"
    exit 1
fi

# 检查虚拟环境是否存在，如果不存在则创建并安装依赖
if [ ! -d "$VENV_DIR" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    echo "安装依赖..."
    pip install -r requirements.txt
else
    # 如果虚拟环境存在，直接激活
    source $VENV_DIR/bin/activate
fi

# 启动Python脚本
echo "启动Python脚本..."
nohup python OVHOrderManager.py > monitor.log 2>&1 &

# 输出进程ID
echo "脚本已在后台运行，日志输出到 monitor.log"
