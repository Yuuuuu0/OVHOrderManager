# OVH 服务器抢购脚本

此脚本用于自动抢购 OVH 提供的云服务器，支持通过 Telegram 和 Bark 发送通知。

## 功能

- 自动监控 OVH 数据中心的可用性。
- 查找特定的服务器配置（如服务器类型、计划等）。
- 自动将符合条件的服务器添加到购物车并完成购买。
- 购买成功后通过 Telegram 或 Bark 发送通知。

## 配置项

在运行此脚本之前，需要根据你的需求配置以下常量：

- **APP_KEY**: 你的 OVH 应用 API Key。
- **APP_SECRET**: 你的 OVH 应用 API Secret。
- **CONSUMER_KEY**: 你的 OVH Consumer Key。
- **REGION**: OVH 数据中心区域（如 `ovh-eu`）。
- **IAM**: 标识用户的名称或 ID（用于发送通知时）。
- **ZONE**: OVH 账号所在的区域（如 `IE`）。
- **TG_TOKEN**: Telegram 机器人 Token。
- **TG_CHAT_ID**: Telegram 频道或用户的 Chat ID。
- **BARK_URL**: Bark 推送的 URL（如果使用 Bark 推送通知）。
- **serverName**: 目标服务器名称（例如 `ks-a`）。
- **planCode**: 目标服务器计划码（例如 `24ska01`）。
- **options**: 需要添加到服务器的额外选项列表。

## 环境依赖

需要安装以下 Python 包：

- `requests`：用于发送 HTTP 请求。
- `logging`：用于日志记录。
- `time`：用于控制任务执行间隔。

可以通过以下命令安装：

```bash
pip install requests
