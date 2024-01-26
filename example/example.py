from observable_properties import observable, subscribe

class Test():
    def __init__(self):
        self._value = 0
    @observable
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value

t = Test()
t.value = 1000
print(t.value)

def observer(instance,property_name,new_value):
    old_value = getattr(instance,property_name)
    print(f"{instance.__class__.__name__}.{property_name} changes from {old_value} to {new_value}")