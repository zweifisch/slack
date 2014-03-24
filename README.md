# slack

a DI Container

## register and provide

```python
from slack import Container

c = Container()

class Component:
    def __init__(self):
        pass

c.register('component', Component)

c1 = c.provide('component')
c2 = c.provide('component')  # c1 is c2
```

## dependency inject

```python
class Component:
    def __init__(self, dep1, dep2):
        pass

c.register('dep1', Dep1)
c.register('dep2', Dep2)
c.register('component', Component)
c.provide('component')
```

## partial inject

```python
class Component:
    def __init__(self, dep1, dep2):
        pass

NewComponent = c.inject(Component, 'dep1')

c = NewComponent(dep2)
```

## using decorator

```python
c.register('comp1')
def comp1(dep1, dep2):
    return SomeClass()
```

## apply

```python
def fn(a, b):
    pass

@c.register('b')
def provide_b():
    pass

c.apply(fn, a=val)
```

## groups and reset

```python
@c.register('comp', group='once')
class Component:
    pass

comp1 = c.provide('comp')
comp2 = c.provide('comp') # comp1 is comp2

c.reset('once')

comp3 = c.provide('comp') # comp3 is not comp2
```
