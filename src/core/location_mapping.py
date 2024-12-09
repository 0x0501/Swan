class LocationMapping():

    def __init__(self, name : str, value : str, literal : str = ''):
        self._name = name
        self._value = value
        self._literal = literal
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value : str):
        self._name = value
        
    @property   
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v : str):
        self._value = v
    
    @property
    def literal(self):
        return self._literal    
    
    @literal.setter
    def literal(self, value : str):
        self._literal = value