#!/bin/bash

PID_FILE="logs/monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "PID 文件不存在，程序可能没有在运行"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null; then
    echo "进程 $PID 已经不存在"
    rm "$PID_FILE"
    exit 1
fi

echo "正在停止进程 $PID..."
kill $PID

# 等待进程结束
for i in {1..5}; do
    if ! ps -p $PID > /dev/null; then
        echo "进程已成功停止"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 如果进程仍然存在，使用 kill -9
if ps -p $PID > /dev/null; then
    echo "进程未响应，强制终止..."
    kill -9 $PID
    if [ $? -eq 0 ]; then
        echo "进程已强制终止"
        rm "$PID_FILE"
        exit 0
    else
        echo "终止进程失败"
        exit 1
    fi
fi 