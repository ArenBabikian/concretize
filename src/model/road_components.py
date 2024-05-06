from abc import ABC, abstractmethod

class Map_Element_Meta_Type():
    def __init__(self):
        pass

    def __str__(self):
        pass

############
class Map_Element_Type():
    def __init__(self):
        # TODO: these instanceOf links may be useless
        self.instanceOf = Map_Element_Meta_Type()

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

class Drivable_Type(Map_Element_Type):

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"Any Drivable Element"

class Road_Type(Drivable_Type, Map_Element_Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"Any Road Elem"
    
class Junction_Type(Drivable_Type, Map_Element_Type):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"Any Junction Elem"

############
class Map_Element_Instance(ABC):

    def __init__(self):
        self.instanceOf = Map_Element_Type()
        self.id = None

    def __repr__(self):
        return str(self)

class Road_Instance(Map_Element_Instance):
    def __init__(self, id):
        super().__init__()
        self.instanceOf = Road_Type()
        self.id = id

    def __str__(self):
        return f"Road {self.id}"


class Junction_Instance(Map_Element_Instance):
    def __init__(self, id):
        super().__init__()
        self.instanceOf = Junction_Type()
        self.id = id

    def __str__(self):
        return f"Junction {self.id}"
