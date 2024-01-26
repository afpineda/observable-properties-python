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
**just before** a property is written in a given object. For example:

```python
def observer(instance,property_name,new_value):
    old_value = getattr(instance,property_name)
    print(f"{instance.__class__.__name__}.{property_name} changes from {old_value} to {new_value}")
```

To start observing a property, call `subscribe()` passing the instance and property name to observe along with the callback function:

```python
from observable_properties import subscribe

subscribe(observer,t,"value")
```

Which means "subscribe `observer` to `t.value`".
Now, the observer is executed whenever the value of the observed property changes at the observed object:

```python
t.value = 2000
```

prints:

```text
Test.value changes from 1000 to 2000
```

Note that:

- Observers **are not allowed** to change the value of the observed property.
  `ObservablePropertyError` is raised in such a case.
- The same observer can subscribe to many objects and properties.
- Any number of observers can subscribe to the same object and property.
  All of them will run. The execution order depends on subscription order.

### Unsubscribe

To stop observing a property, call `unsubscribe()` with the same parameters that were given to `subscribe()`:

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

Observable classes offers another decorator for easier subscription to a single property in a single object:

```python
ot = ObservableTest()
@ot.subscribe("value")
def on_change(new_value):
    old_value = ot.value
    print(f"{ot.__class__.__name__}.value changes from {old_value} to {new_value}")
```

And the `unsubscribe()` **method**:

```python
ot.unsubscribe("value",on_change)
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
