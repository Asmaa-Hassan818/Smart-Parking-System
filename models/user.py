from abc import ABC, abstractmethod

class User(ABC) :
    def __init__(self,user_id,name):
        self.user_id = user_id
        self.name = name

    @abstractmethod
    def get_menu_options(self):
        pass
