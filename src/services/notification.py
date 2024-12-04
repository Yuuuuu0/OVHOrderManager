import logging
import requests
from src.utils.config import config

class NotificationService:
    @staticmethod
    def send_msg(message):
        return NotificationService.send_telegram_msg(message)
        # 如果需要同时发送Bark，可以取消下面的注释
        # return NotificationService.send_telegram_msg(message) and NotificationService.send_bark_notification(message)
    
    @staticmethod
    def send_telegram_msg(message):
        if not config.TG_TOKEN:
            logging.info("TG_TOKEN为空，跳过发送消息")
            return True

        url = f"https://api.telegram.org/bot{config.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": config.TG_CHAT_ID,
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

    @staticmethod
    def send_bark_notification(message):
        if not config.BARK_URL:
            logging.info("BARK_URL为空，跳过发送通知")
            return True

        try:
            response = requests.get(f"{config.BARK_URL}/{message}")
            if response.status_code != 200:
                logging.error(f"Bark通知发送失败: {response.status_code}")
                return False
            return True
        except Exception as e:
            logging.error(f"Bark通知发送异常: {e}")
            return False 