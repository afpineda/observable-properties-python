# Observable object properties

In summary:

- Declare observable properties using the `@observable` decorator instead of `@property`.
- Subscribe/unsubscribe any number of callback functions to observable properties.
- If the value of an observable property changes, all subscribed observers are executed.

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

To start observing a property, call `subscribe()` passing the instance and property name to observe:

```python
from observable_properties import subscribe

subscribe(observer,t,"value")
```

Now, the observer is executed whenever the observed property changes at the observed object:

```python
t.value = 2000
```

It prints:

```text
Test.value changes from 1000 to 2000
```

Note that:

- Observers **are not allowed** to write to the observed property.
  `ObservablePropertyError` is raised otherwise.
- The same observer can subscribe to many objects and properties.
- Any number of observers can subscribe to the same object and property.
  All of them will run. The execution order depends on subscribing order.

### Unsubscribe

To stop observing a property, call `unsubscribe()` with the same parameters that were given to `subscribe()`:

```python
unsubscribe(observer,t,"value")
```

### Syntactic sugar

