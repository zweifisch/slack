from slack import Container, ParamterMissingError
from pytest import raises


class C:
    pass


class D:
    def __init__(self, c):
        self.c = c


class E:
    def __init__(self, d, c):
        self.d = d
        self.c = c


def test_register():
    c = Container()
    c.register('c', C)
    c1 = c.provide('c')
    c2 = c.provide('c')
    assert c1 is c2


def test_reset():
    c = Container()
    c.register('c', C)
    c1 = c.provide('c')
    c.reset()
    c2 = c.provide('c')
    assert c1 is not c2


def test_dependency():
    c = Container()
    c.register('d', D)
    c.register('c', C)
    assert c.provide('d').c is c.provide('c')


def test_group_reset():
    c = Container()
    c.register('d', D)
    c.register('c', C, group='test')
    d1 = c.provide('d')
    c1 = c.provide('c')
    assert d1.c is c1

    c.reset('test')
    d2 = c.provide('d')
    c2 = c.provide('c')
    assert c2 is not c1
    assert d2 is d1


def test_partial_inject():
    c = Container(d=D, c=C)
    F = c.inject(E, 'd', 'c')
    f1 = F()
    assert f1.d.c is f1.c

    F = c.inject(E, 'd')
    f2 = F(c=C())
    assert f2.d.c is not f2.c


def test_apply():
    c = Container(c=C, d=D, e=E)

    def fn(c, d):
        return c is d.c

    assert c.apply(fn)
    assert not c.apply(fn, c=C())

    def fn(c, d, e, f):
        return True

    with raises(ParamterMissingError):
        c.apply(fn)

    assert c.apply(fn, f=None)

    def fn(c, d, e, f=None):
        return True
    assert c.apply(fn)


def test_decorator():
    c = Container()

    @c.register('c')
    def provide_c():
        return True

    assert c.provide('c')
