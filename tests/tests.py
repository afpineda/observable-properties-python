# ****************************************************************************
# @file tests.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-26
# @brief Observable managed attributes
# @copyright 2024. Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from observable_properties import *
from typing import Any
from asyncio import sleep

print("----------------------------------------")
print("observable_properties: Automated test")
print("----------------------------------------")


class Test(Observable):
    def __init__(self):
        self._value = 0
        self._name = "test"

    @observable
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def indirect(self, value):
        self._observable_notify("value", value * 2)

    def indirect_failure(self, value):
        self._observable_notify("name", value * 2)


def assert_obs1(expected):
    global __obs1
    if expected != __obs1:
        print(f"Failure at observer 1: expected {expected}, found {__obs1}")


def assert_obs2(expected):
    global __obs2
    if expected != __obs2:
        print(f"Failure at observer 2: expected {expected}, found {__obs1}")


item = Test()
not_used = Test()


def observer1(instance: object, property_name: str, value: Any):
    global __obs1
    __obs1 = value


def observer_after(instance: object, property_name: str, value: Any):
    if instance != item:
        print("Failure at observer_after: passed instance is not 'item'")
    if property_name != "value":
        print("Failure at observer_after: observable property name is not 'value'")
    global __obs2
    __obs2 = value


def observer_before(instance: object, property_name: str, value: Any):
    global __obs2
    __obs2 = getattr(instance, property_name)
    if instance != item:
        print("Failure at observer_before: passed instance is not 'item'")
    if property_name != "value":
        print("Failure at observer_before: observable property name is not 'value'")


def invalid_observer(instance, name, value):
    item.value = value + 1


async def async_observer(instance: object, property_name: str, value: Any):
    await sleep(1)
    print(f"--   async observer finished: value={value}")


def test_reset():
    global __obs1
    global __obs2
    __obs1 = None
    __obs2 = None
    item.unsubscribe("value", observer1)
    unsubscribe(observer_before, item, "value")
    unsubscribe(observer_after, item, "value")
    unsubscribe(invalid_observer, item, "value")
    unsubscribe(async_observer, item, "value")


print("-- Subscribing to non-observable property")
try:
    item.subscribe("name", observer1)
    print("Failure")
except ObservablePropertyError:
    pass

print("-- Subscribing to non-existing property")
try:
    subscribe(observer1, item, "foo")
    print("Failure")
except ObservablePropertyError:
    pass

print("-- Subscribe first observer and assign value")
test_reset()
item.subscribe("value", observer1)
item.value = 1
assert_obs1(1)
assert_obs2(None)

print("-- Subscribe second observer and assign value")
subscribe(observer_after, item, "value")
item.value = 2
assert_obs1(2)
assert_obs2(2)

print("-- Unsubscribe first observer and assign value")
__obs1 = None
__obs2 = None
item.unsubscribe("value", observer1)
item.value = 3
assert_obs1(None)
assert_obs2(3)

print("-- Unsubscribe second observer and assign value")
__obs1 = None
__obs2 = None
unsubscribe(observer_after, item, "value")
item.value = 3
assert_obs1(None)
assert_obs2(None)

print("-- Unsubscribing second observer again")
if unsubscribe(observer_after, item, "value"):
    print("Failure.")


print("-- Unsubscribing to non-observable property")
try:
    unsubscribe(observer1, item, "name")
    print("Failure.")
except ObservablePropertyError:
    pass

print("-- Unsubscribing to non-existing property")
try:
    unsubscribe(observer1, item, "foo")
    print("Failure.")
except ObservablePropertyError:
    pass


print("-- Testing invalid observer (infinite loop?)")
test_reset()
item.subscribe("value", invalid_observer)
try:
    item.value = 4
except ObservablePropertyError:
    pass
except RecursionError:
    print("Failure")


print("-- Testing callbacks before and after actual value change")
test_reset()
item.value = 5
item.subscribe("value", observer_before, before=True)
item.subscribe("value", observer1)
item.value = 6
assert_obs1(6)
assert_obs2(5)


print("-- Testing async observer (printing for eye-review)")
test_reset()
subscribe(async_observer, item, "value")
item.value = 7

print("-- Testing in-class invalid indirect change")
test_reset()
subscribe(observer1, item, "value")
try:
    item.indirect_failure(1000)
    print("Failure.")
except ObservablePropertyError:
    pass

print("-- Testing in-class indirect change")
item.indirect(1)
assert_obs1(2)

print("--- END ---")
