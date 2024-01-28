# Observable managed attributes (also known as "observable properties")

In summary:

- Declare observable properties using the `@observable` decorator instead of `@property`.
- Subscribe/unsubscribe any number of callback functions to observable properties.
- If the value of an observable property changes, all subscribed callbacks are executed.

## How to use

### Declare observable properties in your class

Use the `@observable` decorator as you do with `@property`:

```python
from observable_properties import observable

class Test():
    def __init__(self):
        self._value = 0
    @observable
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
```

Needless to say, observable properties are also regular properties and they work just the same:

```python
t = Test()
t.value = 1000
print(t.value)
```

### Subscribe to property changes

In the context of this library, an **observer** is a callback function to be executed
when the value of a property is overwritten in a given object. For example:

```python
def observer(instance,property_name,new_value):
    print(f"{instance.__class__.__name__}.{property_name} = {new_value}")
```

To start observing a property, call `subscribe()` passing the instance and property name to observe along with the callback function:

```python
from observable_properties import subscribe

subscribe(observer,t,"value")
```

Which means "subscribe `observer` to `t.value`".
Now, the observer is executed **after** the value of the observed property changes at the observed object:

```python
t.value = 2000
```

prints:

```text
t.value = 2000
```

An observer may also subscribe in this way to be executed **before** the value changes:

```python
def observer_before(instance, property_name, new_value):
    old_value = getattr(instance, property_name)
    print(
        f"{instance.__class__.__name__}.{property_name} changes from {old_value} to {new_value}"
    )
subscribe(observer_before, t, "value",before=True)
t.value = 3000
```

prints:

```text
Test.value changes from 2000 to 3000
Test.value = 3000
```

Note that both `observer` and `observer_before` were executed.

Additionally:

- Observers **are not allowed** to change the value of the observed property.
  `ObservablePropertyError` is raised in such a case.
- The same observer can subscribe to many objects and properties.
- Any number of observers can subscribe to the same object and property.
  All of them will run. The execution order depends on subscription order.
- An observer may be executed before or after a value changes, **but not both**.
  Use different observers for that.

### Unsubscribe

To stop observing a property, call `unsubscribe()` with the same parameters that were given to `subscribe()` (except for `before=`):

```python
from observable_properties import unsubscribe

unsubscribe(observer,t,"value")
```

### Syntactic sugar

To speed things up, derive your class from the `Observable` class (**note the capital letter**).
The declaration itself does not differ too much from the previous example:

```python
from observable_properties import Observable

class ObservableTest(Observable):
    def __init__(self):
        self._value = 0
    @observable
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
```

Observable classes offers `subscribe()` and `unsubscribe()` **methods** with a slightly different
syntax to their function counterparts:

```python
ot = ObservableTest()
ot.subscribe("value",observer)
ot.value = 900
ot.unsubscribe("value", observer)
ot.value = 500
```

prints:

```text
ObservableTest.value = 900
```

## Other notes

- Both `subscribe()` and `unsubscribe()` raise `ObservablePropertyError` on non-observable
  or non-existing properties.
- Subscribing twice to the same object and property has no effect.
- Unsubscribing to non-subscribed properties has no effect, but `unsubscribe()` returns False.
- Objects hold strong references to observers. Deleting an observer does not
  prevent it from running. Unsubscribe first.
- Coroutines are accepted as observers. They are executed by the means of
  [asyncio.run()](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run)
