# OVH 服务器抢购脚本

此脚本用于自动抢购 OVH 提供的云服务器，支持通过 Telegram 和 Bark 发送通知。

## 功能

- 自动监控 OVH 数据中心的可用性
- 支持数据中心优先级配置
- 查找特定的服务器配置（如服务器类型、计划等）
- 自动将符合条件的服务器添加到购物车并完成购买
- 购买成功后通过 Telegram 或 Bark 发送通知
- 详细的日志记录和错误处理

## 系统要求

- Python 3.8+
- Linux/macOS/Windows
- 网络连接
- OVH API 访问权限

## 快速开始

1. 克隆仓库：

```bash
git clone https://github.com/Yuuuuu0/OVHOrderManager.git
cd OVHOrderManager
```

2. 创建配置文件：

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，配置必要的环境变量

4. 运行脚本：

```bash
chmod +x start.sh
./start.sh
```

## 配置说明

在 `.env` 文件中配置以下参数：

### OVH API 配置
- `APP_KEY`: OVH 应用 API Key
- `APP_SECRET`: OVH 应用 API Secret
- `CONSUMER_KEY`: OVH Consumer Key
- `REGION`: OVH 数据中心区域（如 `ovh-eu`）
- `IAM`: 标识用户的名称或 ID
- `ZONE`: OVH 账号所在的区域（如 `IE`）

### 服务器配置
- `SERVER_NAME`: 目标服务器名称（如 `ks-a`）
- `PLAN_CODE`: 目标服务器计划码（如 `24ska01`）
- `OPTIONS`: 需要添加的额外选项，用逗号分隔
- `DATACENTER_PRIORITY`: 数据中心优先级，用逗号分隔（如 `fra,gra`）

### 通知配置
- `TG_TOKEN`: Telegram 机器人 Token
- `TG_CHAT_ID`: Telegram 频道或用户的 Chat ID
- `BARK_URL`: Bark 推送的 URL（可选）

## 目录结构

```
ovh-server-order/
├── src/
│   ├── managers/
│   │   └── ovh_manager.py     # OVH管理核心逻辑
│   ├── services/
│   │   └── notification.py    # 通知服务
│   └── utils/
│       └── config.py          # 配置管理
├── .env.example               # 环境变量示例
├── .gitignore
├── requirements.txt           # 依赖列表
├── main.py                    # 程序入口
└── start.sh                   # 启动脚本
```

## 使用说明

1. 启动脚本：

```bash
./start.sh
```

2. 查看运行日志：

```bash
tail -f monitor.log
```

3. 停止脚本：

```bash
ps aux | grep python3
kill <进程ID>
```

## 注意事项

1. 请确保 OVH API 凭证配置正确
2. 建议先测试通知功能是否正常工作
3. 脚本会在后台运行，可以通过日志文件监控运行状态
4. 成功购买后脚本会自动退出
5. 请确保系统时间准确，这对 API 请求很重要

## 常见问题

1. 如果创建虚拟环境失败，脚本会尝试安装必要的系统包
2. 确保系统有足够的权限执行 sudo 命令
3. 如果收不到通知，请检查通知配置是否正确
4. 如果遇到 API 错误，请检查 API 凭证是否正确

## 获取帮助

如果你在使用过程中遇到任何问题，可以：

1. 查看日志文件了解详细错误信息
2. 提交 Issue 描述你的问题
3. 通过 Pull Request 贡献代码

## 许可证

MIT License
