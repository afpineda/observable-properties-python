# ****************************************************************************
# @file example.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-26
# @brief Observable managed attributes
# @copyright 2024. Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from observable_properties import observable, Observable, subscribe, unsubscribe


class Test:
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
print(f"Current value of t: {t.value}")


def observer(instance, property_name, new_value):
    print(f"{instance.__class__.__name__}.{property_name} = {new_value}")


subscribe(observer, t, "value")
t.value = 2000

class ObservableTest(Observable):
    def __init__(self):
        self._value = 0

    @observable
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


ot = ObservableTest()
ot.subscribe("value", observer)
ot.value = 900
ot.unsubscribe("value", observer)
ot.value = 500

class Product(Observable):
    def __init__(self):
        self._a = 0
        self._b = 0

    @observable
    def value(self):
        return self._a * self._b

    def set(self, a, b):
        with self._observable("value"):
            self._a = a
            self._b = b

    def set_alternate(self, a, b):
        changed = (a!=self._a) or (b!=self._b)
        self._a = a
        self._b = b
        if (changed):
            self._observable_notify("value")

mult = Product()
mult.subscribe("value", observer)
mult.set(3, 5)
mult.set_alternate(4,3)
