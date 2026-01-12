class Order:
    def __init__(self, item, quantity, total):
        self.item = item
        self.quantity = quantity
        self.total = total
        self.id = 1

    def save(self):
        print("Order saved")
