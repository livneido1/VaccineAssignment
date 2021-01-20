class Vaccine:
    def __init__(self, id, date, supplier, quantity):
        self.id = id
        self.date = date
        self.supplier = supplier
        self.quantity = quantity

    def get_id(self):
        return self.id

    def get_date(self):
        return self.date

    def get_supplier(self):
        return self.supplier

    def get_quantity(self):
        return self.quantity