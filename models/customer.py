from models.user import User

class Customer(User):
    def __init__(self , user_id , name):
        super().__init__(user_id, name)

    def park_vehicle(self , vehicle):
        pass

    def exit_vehicle(self , ticket_id):
        pass