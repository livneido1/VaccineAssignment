class Clinic:
    def __init__(self, id, location, demand, logistic):
        self.id = id
        self.location = location
        self.demand = demand
        self.logistic = logistic

    def get_id(self):
        return self.id

    def get_location(self):
        return self.location

    def get_demand(self):
        return self.demand

    def get_logistic(self):
        return self.logistic
