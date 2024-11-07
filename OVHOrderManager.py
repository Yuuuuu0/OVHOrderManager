import logging
import time
import requests
from dotenv import load_dotenv
import os
import ovh
from datetime import datetime, timedelta

# 加载环境变量
load_dotenv()

# 获取配置
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
REGION = os.getenv("REGION")
IAM = os.getenv("IAM")
ZONE = os.getenv("ZONE")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
BARK_URL = os.getenv("BARK_URL")
SERVER_NAME = os.getenv("SERVER_NAME")
PLAN_CODE = os.getenv("PLAN_CODE")
OPTIONS = os.getenv("OPTIONS").split(",")

# 设置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y年%m月%d日 %H:%M:%S',
    handlers=[logging.StreamHandler()]
)

# 初始化OVH客户端
client = ovh.Client(
    endpoint='ovh-eu',
    application_key=APP_KEY,
    application_secret=APP_SECRET,
    consumer_key=CONSUMER_KEY
)


def send_msg(message):
    return send_telegram_msg(message) and send_bark_notification(message)


def send_telegram_msg(message):
    """向指定的 Telegram 发送消息"""
    if not TG_TOKEN:
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
    if not BARK_URL:
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
    try:
        # 获取数据中心的可用性信息
        result = client.get('/dedicated/server/datacenter/availabilities', planCode=PLAN_CODE)
    except ovh.exceptions.APIError as e:
        logging.error(f"获取OVH数据中心可用性时失败: {e}")
        return

    found_available = False
    fqn, plan_code, datacenter = None, None, None

    for item in result:
        if item["planCode"] == PLAN_CODE:
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

                if availability != "unavailable":
                    found_available = True
                    break

            if found_available:
                logging.info(f"正在继续操作，FQN: {fqn} Datacenter: {datacenter}")
                break

    if not found_available:
        logging.info("没有可购买的记录")
        return

    msg = f"{IAM}: 在 {datacenter} 找到 {SERVER_NAME} 可用!"
    if not send_msg(msg):
        logging.error("发送消息通知失败")

    # 创建购物车
    try:
        logging.info("创建购物车")
        # 获取当前UTC时间+1小时
        expire_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        cart_result = client.post('/order/cart', expire=expire_time, ovhSubsidiary=None)
        cart_id = cart_result["cartId"]
        logging.info(f"购物车ID: {cart_id}")
    except ovh.exceptions.APIError as e:
        logging.error(f"创建购物车失败: {e}")
        return

    # 绑定购物车
    try:
        logging.info("绑定购物车")
        client.post(f"/order/cart/{cart_id}/assign")
    except ovh.exceptions.APIError as e:
        logging.error(f"绑定购物车失败: {e}")
        return

    # 将商品添加到购物车
    try:
        logging.info("将商品添加到购物车")
        item_result = client.post(f"/order/cart/{cart_id}/eco", planCode=plan_code, pricingMode="default",
                                  duration="P1M", quantity=1)
        item_id = item_result["itemId"]
        logging.info(f"商品ID: {item_id}")
    except ovh.exceptions.APIError as e:
        logging.error(f"将商品添加到购物车失败: {e}")
        return

    # 获取必需的配置
    try:
        logging.info("检查必需的配置")
        required_config = client.get(f"/order/cart/{cart_id}/item/{item_id}/requiredConfiguration")
    except ovh.exceptions.APIError as e:
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
            client.post(f"/order/cart/{cart_id}/item/{item_id}/configuration", label=config["label"],
                        value=config["value"])
        except ovh.exceptions.APIError as e:
            logging.error(f"配置 {config['label']} 失败: {e}")
            return

    for option in OPTIONS:
        try:
            logging.info(f"添加选项 {option}")
            client.post(f"/order/cart/{cart_id}/eco/options", duration="P1M", itemId=int(item_id), planCode=option,
                        pricingMode="default", quantity=1)
        except ovh.exceptions.APIError as e:
            logging.error(f"添加选项 {option} 失败: {e}")
            return

    # 进行结账
    try:
        logging.info("结账")
        client.get(f"/order/cart/{cart_id}/checkout")
        client.post(f"/order/cart/{cart_id}/checkout", autoPayWithPreferredPaymentMethod=False,
                    waiveRetractationPeriod=True)
    except ovh.exceptions.APIError as e:
        logging.error(f"结账失败: {e}")
        return

    logging.info(f"完成{SERVER_NAME}抢购！")
    msg = f"{IAM}: {SERVER_NAME} 在 {datacenter} 下单成功"
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
