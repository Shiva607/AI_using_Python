from models.order import Order
from utils.logger import log

def create_order(item, quantity, price):
    log("Creating order")

    if quantity <= 0:
        return None

    total = quantity * price
    order = Order(item, quantity, total)
    order.save()

    return order.id
