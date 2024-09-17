from typing import Any, Callable, Generic, Optional, Self, TypeVar
from ctxfn.types import Params, Variables, T

_B = TypeVar("_B")


class FunctionContext(Generic[_B]):
    locals_vars: Variables
    _params_rev: Optional[Callable[..., None]]
    _backto: _B
    current: Any
    _initialize: bool = False

    def __init__(self, backto: _B = None) -> None:
        self.current = None
        self.locals_vars = {}
        self._backto = backto
        self._params_rev = None
        self._initialize = True

    def store(self, name: str, value: Any, as_current=False) -> Self:
        self.locals_vars[name] = value
        if as_current:
            self.current = value
        return self

    def get_current(self) -> Any:
        return self.current

    def set_current(self, current: Any) -> Self:
        self.current = current
        return self

    def set_current_mut(self, generator: Callable[[Any], Any]) -> Self:
        self.current = generator(self.current)
        return self

    def set_local_as_current(self, name: str) -> Self:
        self.current = self.locals_vars[name]
        return self

    def locals_replace(self, factory: Callable[[Self, Variables], Variables]) -> Self:
        self.locals_vars = factory(self, self.locals_vars)
        return self

    def local_mut(self, name: str, factory: Callable[[Self, T], T]) -> Self:
        self.locals_vars[name] = factory(self, self.locals_vars[name])
        return self

    def locals_mut(self, factory: Callable[[Self, Variables], Any]) -> Self:
        factory(self, self.locals_vars)
        return self

    def set_backto_mut(self, backto: _B) -> Self:
        self._backto = backto
        return self

    def set_backto_take(self, backto: T) -> "FunctionContext[T]":
        ctx = FunctionContext(backto)
        ctx.locals_vars = self.locals_vars.copy()
        ctx._params_rev = self._params_rev
        return ctx

    def backto(self) -> _B:
        return self._backto

    def set_params_rev(self, params: Params) -> Self:
        def rev(*args, **kwargs):
            captures = {}
            params_keys = list(params.keys())
            params_keys_max_index = len(params_keys) - 1

            for index, arg in enumerate(args):
                if index > params_keys_max_index:
                    raise Exception("Too many Arguments!")
                arg_name = params_keys[index]
                if params[arg_name].type_check:
                    assert isinstance(
                        arg, params[arg_name].type_expect
                    ), f"Param '{arg_name}' Type Error, Expect: {params[arg_name].type_expect} Got: {type(arg)}"
                captures[arg_name] = arg

            for key, value in kwargs:
                if key in captures:
                    raise Exception(f"DuplicatFe Param! {key}")
                if key not in params:
                    raise Exception(f"Unknown Param! {key}")
                if params[key].type_check:
                    assert isinstance(
                        value, params[key].type_expect
                    ), f"Param '{key}' Type Error, Expect: {params[key].type_expect} Got: {type(value)}"
                captures[key] = value

            if len(captures) != len(params):
                start_index = len(args) - 1

                for name, param in list(params.items())[start_index::]:
                    if not param.hasdefault:
                        raise Exception(f"Param: {key} has no default value")
                    if name not in captures:
                        captures[name] = param.default

                if len(captures) != len(params):
                    captures_key_set = set(captures.keys())
                    params_key_set = set(params.keys())

                    raise Exception(
                        f"Params can't match! required: {params_key_set - (captures_key_set|params_key_set)}"
                    )
            self.locals_vars.update(captures)

        self._params_rev = rev

        return self
