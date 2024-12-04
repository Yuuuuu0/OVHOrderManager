from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        
        # OVH配置
        self.APP_KEY = os.getenv("APP_KEY")
        self.APP_SECRET = os.getenv("APP_SECRET")
        self.CONSUMER_KEY = os.getenv("CONSUMER_KEY")
        self.REGION = os.getenv("REGION")
        self.IAM = os.getenv("IAM")
        self.ZONE = os.getenv("ZONE")
        
        # 服务器配置
        self.SERVER_NAME = os.getenv("SERVER_NAME")
        self.PLAN_CODE = os.getenv("PLAN_CODE")
        self.OPTIONS = os.getenv("OPTIONS", "").split(",")
        self.DATACENTER_PRIORITY = os.getenv("DATACENTER_PRIORITY", "fra,gra").split(",")
        
        # 通知配置
        self.TG_TOKEN = os.getenv("TG_TOKEN")
        self.TG_CHAT_ID = os.getenv("TG_CHAT_ID")
        self.BARK_URL = os.getenv("BARK_URL")

config = Config() 