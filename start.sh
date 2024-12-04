#!/bin/bash

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "错误：.env 文件不存在！"
    echo "请先创建 .env 文件并配置必要的环境变量"
    echo "可以复制 .env.example 作为模板："
    echo "cp .env.example .env"
    exit 1
fi

# 安装必要的系统包
install_requirements() {
    echo "检查并安装必要的系统包..."
    sudo apt update
    sudo apt install -y python3-venv python3-pip
}

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    # 如果创建虚拟环境失败，安装依赖后重试
    if ! python3 -m venv venv; then
        install_requirements
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 只在首次创建虚拟环境时安装依赖
    echo "安装依赖..."
    pip install -r requirements.txt
else
    # 虚拟环境存在，直接激活
    source venv/bin/activate
fi

# 启动Python脚本
echo "启动Python脚本..."
nohup python3 main.py > monitor.log 2>&1 &

echo "脚本已在后台运行，日志输出到 monitor.log"
echo "使用 'tail -f monitor.log' 查看实时日志"