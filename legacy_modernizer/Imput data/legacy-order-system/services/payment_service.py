from utils.logger import log

def process_payment(order_id, method):
    log("Processing payment")

    if method == "CREDIT_CARD":
        return True
    elif method == "CASH":
        return True
    else:
        return False
