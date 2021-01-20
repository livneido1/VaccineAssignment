class Supplier:
    def __init__(self, id, name, logistic):
        self.id = id
        self.name = name
        self.logistic = logistic

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_logistic(self):
        return self.logistic
