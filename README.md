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
print(f"Current value of t: {t.value}")
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
Now, the observer is executed after the value of the observed property changes at the observed object:

```python
t.value = 2000
```

prints:

```text
Test.value = 2000
```

Additionally:

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

In order to unsubscribe from all observable properties, pass an empty string (`""`) as the property name.

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

Observable classes offer `subscribe()` and `unsubscribe()` **methods** with a slightly different
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

#### Observable changes triggered from *non-setter* methods

A public *setter* is **not mandatory** for observable properties of an `Observable` instance.
This is a common use case for computed properties.

Any method can notify changes in observable properties in two ways:

- Compute the new value inside the context returned by `self._observable()`.
  The new value is automatically notified to all subscribers on exit.
  As an example, see `Product.set()` below.
- Explicitly call `self._observable_notify()` after the computation is finished.
  As an example, see `Product.set_alternate()` below.

```python
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
```

prints:

```text
Product.value = 15
Product.value = 12
```

## Other notes

- `subscribe()`, `unsubscribe()`, `_observable()` and `_observable_notify()`
  raise `ObservablePropertyError` on non-observable or non-existing properties.
- Subscribing twice to the same object and property has no effect.
- Unsubscribing to non-subscribed properties has no effect, but `unsubscribe()` returns False.
- Objects hold strong references to observers. Deleting an observer does not
  prevent it from running. Unsubscribe first.
- Coroutines are accepted as observers. They are executed by the means of
  [asyncio.run()](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run)
