import inspect
import sys
from functools import partial
from collections import defaultdict
import importlib

if sys.version_info < (3, 4):
    def _no_args():
        pass

    def getargspec(obj):
        if inspect.isclass(obj):
            if hasattr(obj, '__init__'):
                return inspect.getargspec(obj.__init__)
            else:
                return inspect.getargspec(_no_args)
        else:
            return inspect.getargspec(obj)
else:
    getargspec = inspect.getargspec


class Container:

    def __init__(self, protos=None, **kwargs):
        self.__protos__ = protos or kwargs or {}
        self.__groups__ = defaultdict(list)
        self.__params__ = {}
        self.__conf__ = {}
        self.__resolving__ = {}

    def __getattr__(self, name):
        if name not in self.__protos__ and name not in self.__conf__:
            raise AttributeError("%s not registered" % name)
        return self.provide(name)

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]

    def register(self, name, value=None, group='default'):
        if value is None:
            return partial(self.register, name, group=group)
        self.__protos__[name] = value
        self.__groups__[group].append(name)
        return value

    def accessed(self, name):
        return name in self.__dict__

    def provide(self, name):
        if name in self.__resolving__:
            raise CircularDependencyError("%s is required while providing %s"
                                          % (name, name))
        self.__resolving__[name] = True
        if name not in self.__dict__:
            if name in self.__conf__:
                modulename, cls = self.__conf__[name].split(':')
                module = importlib.import_module(modulename)
                self.__protos__[name] = getattr(module, cls)
            if name not in self.__protos__:
                raise ComponentNotRegisteredError("%s not registered" % name)
            if type(self.__protos__[name]) is tuple:
                cls, params = self.__protos__[name]
                self.__dict__[name] = invoke(cls, params, self)
            else:
                args = getargspec(self.__protos__[name]).args
                conf = {}
                if args and self.__conf__:
                    for arg in args:
                        if "%s_%s" % (name, arg) in self.__conf__:
                            conf[arg] = self.__conf__["%s_%s" % (name, arg)]
                self.__dict__[name] = invoke(self.__protos__[name], conf, self)
        del self.__resolving__[name]
        return self.__dict__[name]

    def reset(self, group='default'):
        for name in self.__groups__[group]:
            if name in self.__dict__:
                del self.__dict__[name]

    def inject(self, cls, *args):
        params = {}
        for arg in args:
            params[arg] = self.provide(arg)
        return partial(cls, **params)

    def apply(self, fn, **kwargs):
        return invoke(fn, kwargs, self)

    def config(self, conf):
        for key, value in conf.items():
            self.__conf__[key] = value


class CircularDependencyError(Exception):
    pass


class ComponentNotRegisteredError(Exception):
    pass


class ParamterMissingError(Exception):
    pass


def invoke(fn, *param_dicts):
    "call a function with a list of dicts providing params"
    spec = getargspec(fn)
    if not spec.args:
        return fn()

    prepared_params = {}
    if spec.defaults is None:
        defaults = {}
    else:
        defaults = dict(zip(spec.args[-len(spec.defaults):], spec.defaults))
    args = spec.args[1:] if spec.args[0] == 'self' else spec.args
    for name in args:
        for params in param_dicts:
            if type(params) is dict and name in params:
                prepared_params[name] = params[name]
                break
            elif hasattr(params, name):
                prepared_params[name] = getattr(params, name)
                break
        if name not in prepared_params:
            if name not in defaults:
                raise ParamterMissingError("%s is required when calling %s" %
                                           (name, fn.__name__))
    return fn(**prepared_params)

__all__ = ['Container', 'ComponentNotRegisteredError', 'ParamterMissingError']
