import logging
import ovh
from datetime import datetime, timedelta, timezone
from src.utils.config import config
from src.services.notification import NotificationService

class OVHManager:
    def __init__(self):
        self.client = ovh.Client(
            endpoint=config.REGION,
            application_key=config.APP_KEY,
            application_secret=config.APP_SECRET,
            consumer_key=config.CONSUMER_KEY
        )
        self.notification = NotificationService()

    def run_task(self):
        """执行OVH服务器购买任务"""
        try:
            datacenter = self._check_availability()
            if not datacenter:
                return

            cart_id, item_id = self._create_and_configure_cart(datacenter)
            if not cart_id or not item_id:
                return

            self._checkout_cart(cart_id, datacenter)
            
        except Exception as e:
            logging.error(f"任务执行失败: {e}")
            return

    def _check_availability(self):
        """检查服务器可用性"""
        try:
            result = self.client.get('/dedicated/server/datacenter/availabilities', 
                                   planCode=config.PLAN_CODE)
        except ovh.exceptions.APIError as e:
            logging.error(f"获取OVH数据中心可用性时失败: {e}")
            return None

        found_available = False
        fqn, plan_code, datacenter = None, None, None

        # 定义优先级
        priority = {dc: idx + 1 for idx, dc in enumerate(config.DATACENTER_PRIORITY)}

        for item in result:
            if item["planCode"] == config.PLAN_CODE:
                fqn = item["fqn"]
                plan_code = item["planCode"]
                datacenters = item["datacenters"]

                # 按照优先级排序
                datacenters.sort(key=lambda dc: priority.get(dc["datacenter"], 999))

                for dc_info in datacenters:
                    availability = dc_info["availability"]
                    datacenter = dc_info["datacenter"]
                    logging.info(f"FQN: {fqn}")
                    logging.info(f"Availability: {availability}")
                    logging.info(f"Datacenter: {datacenter}")
                    logging.info("------------------------")

                    if availability != "unavailable" and "coming" not in availability:
                        found_available = True
                        break

                if found_available:
                    msg = f"{config.IAM}: 在 {datacenter} 找到 {config.SERVER_NAME} 可用!"
                    self.notification.send_msg(msg)
                    return datacenter

        logging.info("没有可购买的记录")
        return None

    def _create_and_configure_cart(self, datacenter):
        """创建和配置购物车"""
        try:
            # 创建购物车
            expire_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            cart_result = self.client.post('/order/cart', 
                                         expire=expire_time, 
                                         ovhSubsidiary=config.ZONE)
            cart_id = cart_result["cartId"]
            logging.info(f"购物车ID: {cart_id}")

            # 绑定购物车
            self.client.post(f"/order/cart/{cart_id}/assign")

            # 添加商品到购物车
            item_result = self.client.post(f"/order/cart/{cart_id}/eco", 
                                         planCode=config.PLAN_CODE,
                                         pricingMode="default",
                                         duration="P1M",
                                         quantity=1)
            item_id = item_result["itemId"]
            logging.info(f"商品ID: {item_id}")

            # 配置必需的选项
            required_config = self.client.get(f"/order/cart/{cart_id}/item/{item_id}/requiredConfiguration")
            
            # 获取region值
            region_value = None
            for config_item in required_config:
                if config_item["label"] == "region":
                    allowed_values = config_item["allowedValues"]
                    if allowed_values:
                        region_value = allowed_values[0]

            # 配置基本选项
            configurations = [
                {"label": "dedicated_datacenter", "value": datacenter},
                {"label": "dedicated_os", "value": "none_64.en"},
                {"label": "region", "value": region_value},
            ]

            # 应用配置
            for conf in configurations:
                self.client.post(f"/order/cart/{cart_id}/item/{item_id}/configuration",
                               label=conf["label"],
                               value=conf["value"])

            # 添加额外选项
            for option in config.OPTIONS:
                self.client.post(f"/order/cart/{cart_id}/eco/options",
                               duration="P1M",
                               itemId=int(item_id),
                               planCode=option,
                               pricingMode="default",
                               quantity=1)

            return cart_id, item_id

        except ovh.exceptions.APIError as e:
            logging.error(f"购物车操作失败: {e}")
            return None, None

    def _checkout_cart(self, cart_id, datacenter):
        """完成购物车结账"""
        try:
            self.client.get(f"/order/cart/{cart_id}/checkout")
            self.client.post(f"/order/cart/{cart_id}/checkout",
                           autoPayWithPreferredPaymentMethod=False,
                           waiveRetractationPeriod=True)

            logging.info(f"完成{config.SERVER_NAME}抢购！")
            msg = f"{config.IAM}: {config.SERVER_NAME} 在 {datacenter} 下单成功"
            if not self.notification.send_msg(msg):
                logging.error("发送购买成功通知失败")

            exit(0)  # 成功后退出脚本

        except ovh.exceptions.APIError as e:
            logging.error(f"结账失败: {e}")
            self.delete_cart(cart_id)
            raise e

    def check_cart_exists(self, cart_id):
        """检查购物车是否存在"""
        try:
            result = self.client.get(f"/order/cart/{cart_id}")
            logging.info(f"购物车 {cart_id} 存在")
            return True
        except Exception as e:
            if "Cart not found" in str(e):
                logging.info(f"购物车 {cart_id} 不存在")
                return False
            logging.error(f"检查购物车 {cart_id} 状态时发生错误: {str(e)}")
            raise e

    def delete_cart(self, cart_id):
        """删除购物车"""
        try:
            if self.check_cart_exists(cart_id):
                logging.info(f"开始删除购物车 {cart_id}")
                self.client.delete(f"/order/cart/{cart_id}")
                logging.info(f"购物车 {cart_id} 删除成功")
                return True
            logging.info(f"购物车 {cart_id} 不存在，无需删除")
            return False
        except Exception as e:
            logging.error(f"删除购物车 {cart_id} 失败: {str(e)}")
            raise e