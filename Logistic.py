class Logistic:
    def __init__(self , id , name , count_sent , count_received ):
        self.id = id
        self.name = name
        self.count_sent = count_sent
        self.count_received = count_received

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_count_sent(self):
        return self.count_sent

    def get_count_received(self):
        return self.count_received