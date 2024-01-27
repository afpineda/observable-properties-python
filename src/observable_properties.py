# ****************************************************************************
# @file observable_properties.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-26
# @brief Observable managed attributes
# @copyright 2024. Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

"""Observable object properties

Declare observable properties using the `@observable` decorator instead of `@property`.
Subscribe/unsubscribe any number of callback functions to observable properties.
If the value of an observable property changes, all subscribed observers are executed.

Functions:
    subscribe(): subscribe a callback to changes in observable properties.
    unsubscribe(): unsubscribe a callback from changes in observable properties.

Classes:
    Observable: helper class for easy subscription to observable properties.

Types:
    Observer: callback prototype for observable properties.
    InstanceObserver: callback prototype for known observable properties in known objects.

Exceptions:
    ObservablePropertyError: for invalid operations on observable object properties.
"""

# *****************************************************************************
# "Exports"
# *****************************************************************************

__all__ = [
    "subscribe",
    "unsubscribe",
    "Observable",
    "observable",
]

# *****************************************************************************
# Imports
# *****************************************************************************

from typing import Callable, Any
from functools import wraps
from inspect import iscoroutinefunction
from asyncio import run

# *****************************************************************************
# Types
# *****************************************************************************

Observer = Callable[[object, str, Any], None]
"""Callback prototype for observable properties.

Called just before the property's value is actually modified.

Args:
    instance (object): object being observed
    property_name (str): name of the property that is about to change
    value (Any): new value of the property

Raises:
    ObservablePropertyError: attempt to modify the property being observed.
"""

InstanceObserver = Callable[[Any], None]
"""Callback prototype for known observable properties in known objects.

Called just before the property's value is actually modified.

Args:
    value (Any): new value of the property

Raises:
    ObservablePropertyError: attempt to modify the property being observed.
"""

# *****************************************************************************
# Exceptions
# *****************************************************************************


class ObservablePropertyError(Exception):
    """Exception for invalid operations on observable object properties."""

    pass


# *****************************************************************************
# Classes
# *****************************************************************************


class observable(property):
    def __set__(self, __instance: Any, __value: Any) -> None:
        subscribers = getattr(__instance, self.subscribers)
        recursions = getattr(__instance, self.recursions)
        try:
            for observer in subscribers:
                if observer not in recursions:
                    recursions.append(observer)
                    if iscoroutinefunction(observer):
                        run(observer(__instance, self.observable_property, __value))
                    else:
                        observer(__instance, self.observable_property, __value)
                else:
                    raise ObservablePropertyError(
                        f"'{observer.__name__}' is not allowed to modify observable property "
                        + f"'{__instance.__class__.__name__}.{self.observable_property}'"
                    )
        finally:
            recursions.clear()
        super().__set__(__instance, __value)

    def __delete__(self, __instance: Any) -> None:
        super().__delete__(__instance)
        delattr(__instance, self.subscribers)
        delattr(__instance, self.recursions)

    def __set_name__(self, owner, owner_name):
        self.observable_property = owner_name
        self.subscribers = "__" + owner_name + "_subscribers"
        self.recursions = "__" + owner_name + "_recursions"
        if not hasattr(owner, self.subscribers):
            setattr(owner, self.subscribers, [])
        if not hasattr(owner, self.recursions):
            setattr(owner, self.recursions, [])


class Observable:
    """Helper class for easy subscription to observable properties."""

    def unsubscribe(self, property_name: str, callback: Observer) -> bool:
        """Unsubscribe a callback from changes in an observable property of this object.

        Args:
            callback (Callable[[object, str, Any], None]): _description_
            property_name (str): _description_

        Returns:
            bool: True on success. If false, the property is not observable or
                  the callback was not subscribed.
        """
        return unsubscribe(callback, self, property_name)

    def subscribe(self, property_name: str) -> None:
        """Decorator to subscribe a callback to an observable property of this object.

        Args:
            property_name (str): name of the property to observe in this object

        Raises:
            ObservablePropertyError: if the requested property is not observable
        """

        def wrapper(func: InstanceObserver):
            @wraps(func)
            def callback(instance: object, name: str, value: Any):
                if iscoroutinefunction(func):
                    return run(func(value))
                else:
                    return func(value)

            subscribe(callback, self, property_name)
            return callback

        return wrapper


# *****************************************************************************
# "public" functions
# *****************************************************************************


def subscribe(callback: Observer, instance: object, property_name: str) -> None:
    """Subscribe a callback to changes in observable properties.

    Args:
        callback (Callable[[object, str, Any], None]): function to be called.
        instance (object): instance to observe.
        property_name (str): name of the property to observe at the given instance.

    Raises:
        ObservablePropertyError: if the requested property is not observable.
    """
    subscribers_attr_name = "__" + property_name + "_subscribers"
    if hasattr(instance, subscribers_attr_name):
        subscribers = getattr(instance, subscribers_attr_name)
        if not callback in subscribers:
            subscribers.append(callback)
    else:
        raise ObservablePropertyError(
            f"{property_name} is not an observable property of {instance.__class__.__name__}"
        )


def unsubscribe(callback: Observer, instance: object, property_name: str) -> bool:
    """Unsubscribe a callback from changes in observable properties.

    Args:
        callback (Callable[[object, str, Any], None]): function to unsubscribe.
        instance (object): observed instance.
        property_name (str): name of the observed property at the given instance.

    Returns:
         bool: True on success. False if the callback was not subscribed.

    Raises:
        ObservablePropertyError: if the requested property is not observable.
    """
    subscribers_attr_name = "__" + property_name + "_subscribers"
    if hasattr(instance, subscribers_attr_name):
        subscribers = getattr(instance, subscribers_attr_name)
        if callback in subscribers:
            subscribers.remove(callback)
            return True
        return False
    else:
        raise ObservablePropertyError(
            f"{property_name} is not an observable property of {instance.__class__.__name__}"
        )


# *****************************************************************************
# Automated Test
# *****************************************************************************

if __name__ == "__main__":
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

    def test_reset():
        global __obs1
        global __obs2
        __obs1 = None
        __obs2 = None

    def assert_obs1(expected):
        if expected != __obs1:
            print(f"Failure at observer 1: expected {expected}, found {__obs1}")

    def assert_obs2(expected):
        if expected != __obs2:
            print(f"Failure at observer 2: expected {expected}, found {__obs1}")

    item = Test()
    not_used = Test()

    print("-- Subscribing observer 1")

    @item.subscribe("value")
    def observer1(value):
        global __obs1
        __obs1 = value

    print("-- Subscribing observer 2")

    def observer2(instance: object, property_name: str, value: Any):
        if instance != item:
            print("Failure at observer2: passed instance is not 'item'")
        if property_name != "value":
            print("Failure at observer2: observable property name is not 'value'")
        global __obs2
        __obs2 = value

    subscribe(observer2, item, "value")

    print("-- Subscribing to non-observable property")
    try:

        @item.subscribe("name")
        def non_valid1(value):
            pass

        print("Failure #1")
    except ObservablePropertyError:
        pass
    try:
        subscribe(observer2, item, "name")
        print("Failure #2")
    except ObservablePropertyError:
        pass

    print("-- Subscribing to non-existing property")
    try:

        @item.subscribe("foo")
        def non_valid2(value):
            pass

        print("Failure #1")
    except ObservablePropertyError:
        pass
    try:
        subscribe(observer2, item, "foo")
        print("Failure #2")
    except ObservablePropertyError:
        pass

    print("-- Assign value to observable property")
    test_reset()
    item.value = 1
    assert_obs1(1)
    assert_obs2(1)

    print("-- Unsubscribing observer 2")
    test_reset()
    unsubscribe(observer2, item, "value")
    item.value = 2
    assert_obs1(2)
    assert_obs2(None)

    print("-- Unsubscribing observer 1")
    test_reset()
    item.unsubscribe("value", observer1)
    item.value = 3
    assert_obs1(None)
    assert_obs2(None)

    print("-- Unsubscribing observer 2 again")
    if unsubscribe(observer2, item, "value"):
        print("Failure.")

    print("-- Unsubscribing to non-observable property")
    try:
        unsubscribe(observer2, item, "name")
        print("Failure.")
    except:
        pass

    print("-- Unsubscribing to non-existing property")
    try:
        unsubscribe(observer2, item, "foo")
        print("Failure.")
    except:
        pass

    print("-- Subscribing observer 3")

    @item.subscribe("value")
    def observer3(value):
        item.value = value + 1

    print("-- Testing observer 3 behavior (infinite loop?)")
    try:
        item.value = 4
    except ObservablePropertyError:
        pass
    item.unsubscribe("value", observer3)

    print("-- Testing async observer 4 (printing for eye-review)")
    from asyncio import sleep

    async def observer4(instance: object, property_name: str, value: Any):
        await sleep(1)
        print(f"--   observer 4 finished: value={value}")

    subscribe(observer4, item, "value")
    item.value = 5
    unsubscribe(observer4, item, "value")

    print("-- Testing async observer 5 (printing for eye-review)")

    @item.subscribe("value")
    async def observer5(value: Any):
        await sleep(1)
        print(f"--   observer 5 finished: value={value}")

    item.value = 6
    item.unsubscribe("value", observer5)

    print("--- END ---")
