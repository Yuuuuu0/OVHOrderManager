import logging
import time

import requests

# 常量定义
APP_KEY = ""
APP_SECRET = ""
CONSUMER_KEY = ""
REGION = "ovh-eu"
IAM = "python-ovh-ie"
ZONE = "IE"
# 推送配置
TG_TOKEN = ""
TG_CHAT_ID = ""
BARK_URL = ""

# 需要抢购的配置
serverName = "ks-a"
planCode = "24ska01"
options = [
    "bandwidth-100-24sk",
    "ram-64g-noecc-2133-24ska01",
    "softraid-1x480ssd-24ska01"
]

# 设置日志输出
logging.basicConfig(
    level=logging.INFO,  # 记录INFO及以上级别的日志
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y年%m月%d日 %H:%M:%S',  # 日期时间格式
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        # logging.FileHandler('monitor.log')  # 同时输出到文件
    ]
)


def send_msg(message):
    return send_telegram_msg(message) and send_bark_notification(message)


def send_telegram_msg(message):
    """向指定的 Telegram 发送消息"""
    if not TG_TOKEN:  # 如果TG_TOKEN为空，直接返回True
        logging.info("TG_TOKEN为空，跳过发送消息")
        return True

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        if response.status_code != 200:
            logging.error(f"发送消息失败: {response.status_code}, {response.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"发送Telegram消息时发生错误: {e}")
        return False


def send_bark_notification(message):
    """向指定的Bark发送通知"""
    if not BARK_URL:  # 如果BARK_URL为空，直接返回True
        logging.info("BARK_URL为空，跳过发送通知")
        return True

    try:
        response = requests.get(f"{BARK_URL}/{message}")
        if response.status_code != 200:
            logging.error(f"Bark通知发送失败: {response.status_code}")
            return False
        return True
    except Exception as e:
        logging.error(f"Bark通知发送异常: {e}")
        return False


def run_task():
    """执行任务，检查OVH的可用性并处理购买流程"""
    # 创建OVH API客户端
    try:
        # 获取数据中心的可用性信息
        url = f"https://api.ovh.com/1.0/dedicated/server/datacenter/availabilities"
        headers = {
            "X-Ovh-Application": APP_KEY,
            "X-Ovh-Consumer": CONSUMER_KEY
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()  # 解析返回的JSON数据
    except requests.exceptions.RequestException as e:
        logging.error(f"获取OVH数据中心可用性时失败: {e}")
        return

    found_available = False
    fqn, plan_code, datacenter = None, None, None

    for item in result:
        if item["planCode"] == planCode:  # 如果找到了符合条件的计划
            fqn = item["fqn"]
            plan_code = item["planCode"]
            datacenters = item["datacenters"]

            for dc_info in datacenters:
                availability = dc_info["availability"]
                datacenter = dc_info["datacenter"]
                logging.info(f"FQN: {fqn}")
                logging.info(f"Availability: {availability}")
                logging.info(f"Datacenter: {datacenter}")
                logging.info("------------------------")

                if availability != "unavailable":  # 如果该数据中心是可用的
                    found_available = True
                    break

            if found_available:
                logging.info(f"正在继续操作，FQN: {fqn} Datacenter: {datacenter}")
                break

    if not found_available:
        logging.info("没有可购买的记录")
        return

    msg = f"{IAM}: 在 {datacenter} 找到 {serverName} 可用!"
    if not send_msg(msg):
        logging.error("发送消息通知失败")

    # 创建购物车
    try:
        logging.info("创建购物车")
        url = f"https://api.ovh.com/1.0/order/cart"
        payload = {"ovhSubsidiary": ZONE}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        cart_result = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"创建购物车失败: {e}")
        return

    cart_id = cart_result["cartId"]
    logging.info(f"购物车ID: {cart_id}")

    # 绑定购物车
    try:
        logging.info("绑定购物车")
        url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/assign"
        response = requests.post(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"绑定购物车失败: {e}")
        return

    # 将商品添加到购物车
    try:
        logging.info("将商品添加到购物车")
        url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/eco"
        payload = {
            "planCode": plan_code,
            "pricingMode": "default",
            "duration": "P1M",  # 持续时间为1个月
            "quantity": 1
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        item_result = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"将商品添加到购物车失败: {e}")
        return

    item_id = item_result["itemId"]
    logging.info(f"商品ID: {item_id}")

    # 获取必需的配置
    try:
        logging.info("检查必需的配置")
        url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/item/{item_id}/requiredConfiguration"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        required_config = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"获取必需配置失败: {e}")
        return

    dedicated_os = "none_64.en"
    region_value = None
    for config in required_config:
        if config["label"] == "region":
            allowed_values = config["allowedValues"]
            if allowed_values:
                region_value = allowed_values[0]

    configurations = [
        {"label": "dedicated_datacenter", "value": datacenter},
        {"label": "dedicated_os", "value": dedicated_os},
        {"label": "region", "value": region_value},
    ]

    # 配置购物车中的商品
    for config in configurations:
        try:
            logging.info(f"配置 {config['label']}")
            url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/item/{item_id}/configuration"
            payload = {"label": config["label"], "value": config["value"]}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"配置 {config['label']} 失败: {e}")
            return

    for option in options:
        try:
            logging.info(f"添加选项 {option}")
            url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/eco/options"
            payload = {
                "duration": "P1M",  # 选项持续时间为1个月
                "itemId": int(item_id),
                "planCode": option,
                "pricingMode": "default",
                "quantity": 1
            }
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"添加选项 {option} 失败: {e}")
            return

    # 进行结账
    try:
        logging.info("结账")
        url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/checkout"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        checkout_result = response.json()

        # 提交结账请求
        url = f"https://api.ovh.com/1.0/order/cart/{cart_id}/checkout"
        payload = {
            "autoPayWithPreferredPaymentMethod": False,
            "waiveRetractationPeriod": True
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"结账失败: {e}")
        return

    logging.info(f"完成{serverName}抢购！")
    msg = f"{IAM}: {serverName} 在 {datacenter} 下单成功"
    if not send_msg(msg):
        logging.error("发送购买成功通知失败")

    exit(0)  # 结束脚本


def main():
    """主函数：循环执行任务"""
    while True:
        run_task()  # 执行任务
        time.sleep(5)  # 每n秒执行一次任务


if __name__ == "__main__":
    main()
