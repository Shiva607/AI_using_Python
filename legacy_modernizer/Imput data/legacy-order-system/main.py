from services.order_service import create_order
from services.payment_service import process_payment

def main():
    order_id = create_order("Laptop", 2, 50000)
    result = process_payment(order_id, "CREDIT_CARD")

    if result == True:
        print("Order completed")
    else:
        print("Payment failed")

main()
