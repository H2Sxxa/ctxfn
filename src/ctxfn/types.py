from typing import Any, Dict, Generic, OrderedDict, ParamSpec, Type, TypeVar


Variables = Dict[str, Any]
T = TypeVar("T")
P = ParamSpec("P")


class Param(Generic[T]):
    name: str
    hasdefault: bool
    default: T
    type_expect: Type[T]
    type_check: False

    @staticmethod
    def new(name: str, type_check=False, type_expect=Any) -> "Param":
        param = Param()
        param.name = name
        param.hasdefault = True
        param.default = None
        param.type_check = type_check
        param.type_expect = type_expect
        return param

    @staticmethod
    def default(name: str, default: T, type_check=False, type_expect=Any) -> "Param[T]":
        param = Param()
        param.name = name
        param.hasdefault = True
        param.type_check = type_check
        param.type_expect = type_expect
        if type_check:
            assert isinstance(
                default, type_expect
            ), f"Default Type Error, Expect: {type_expect}, Got: {type(default)}"

        param.default = default
        return param


Params = OrderedDict[str, Param]
