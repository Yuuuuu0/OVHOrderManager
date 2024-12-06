import logging
from src.managers.ovh_manager import OVHManager

class CartCleaner:
    def __init__(self):
        self.ovh_manager = OVHManager()

    def clean_all_carts(self):
        """
        清理所有购物车
        
        Returns:
            tuple: (成功删除数量, 失败删除数量)
        """
        try:
            # 获取所有购物车
            carts = self.ovh_manager.client.get("/order/cart")
            
            success_count = 0
            failed_count = 0
            
            for cart_id in carts:
                try:
                    if self.ovh_manager.delete_cart(cart_id):
                        success_count += 1
                        logging.info(f"成功删除购物车: {cart_id}")
                    else:
                        failed_count += 1
                        logging.warning(f"购物车不存在或已被删除: {cart_id}")
                except Exception as e:
                    failed_count += 1
                    logging.error(f"删除购物车 {cart_id} 失败: {str(e)}")
            
            logging.info(f"购物车清理完成 - 成功: {success_count}, 失败: {failed_count}")
            return success_count, failed_count
            
        except Exception as e:
            logging.error(f"获取购物车列表失败: {str(e)}")
            raise e

    def clean_expired_carts(self):
        """
        清理已过期的购物车
        
        Returns:
            tuple: (成功删除数量, 失败删除数量)
        """
        try:
            # 获取所有购物车
            carts = self.ovh_manager.client.get("/order/cart")
            
            success_count = 0
            failed_count = 0
            
            for cart_id in carts:
                try:
                    # 获取购物车详情
                    cart_info = self.ovh_manager.client.get(f"/order/cart/{cart_id}")
                    
                    # 如果购物车已过期，则删除
                    if cart_info.get("expire") and cart_info.get("readOnly"):
                        if self.ovh_manager.delete_cart(cart_id):
                            success_count += 1
                            logging.info(f"成功删除过期购物车: {cart_id}")
                        else:
                            failed_count += 1
                            logging.warning(f"过期购物车不存在或已被删除: {cart_id}")
                            
                except Exception as e:
                    failed_count += 1
                    logging.error(f"处理购物车 {cart_id} 失败: {str(e)}")
            
            logging.info(f"过期购物车清理完成 - 成功: {success_count}, 失败: {failed_count}")
            return success_count, failed_count
            
        except Exception as e:
            logging.error(f"获取购物车列表失败: {str(e)}")
            raise e 