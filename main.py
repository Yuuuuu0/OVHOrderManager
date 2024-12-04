import logging
import time
from src.managers.ovh_manager import OVHManager

# 设置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y年%m月%d日 %H:%M:%S',
    handlers=[logging.StreamHandler()]
)

def main():
    """主函数：循环执行任务"""
    manager = OVHManager()
    while True:
        manager.run_task()
        time.sleep(5)

if __name__ == "__main__":
    main() 