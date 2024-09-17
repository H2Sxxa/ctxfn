from typing import Any, OrderedDict, Self
from ctxfn.context import FunctionContext
from ctxfn.expression.execute import FunctionOpsBuilder
from ctxfn.types import Params, Param


class DefineBuilder:
    _params: Params
    _ctx: FunctionContext[Self]

    def __init__(self) -> None:
        self._params = OrderedDict()
        self._ctx = FunctionContext(self)

    def arg(self, name: str, type_check=False, type_expect=Any) -> Self:
        self._params[name] = Param.new(
            name,
            type_check=type_check,
            type_expect=type_expect,
        )
        return self

    def args(self, *args):
        self._params.update({name: Param.new(name) for name in args})
        return self

    def kwarg(self, name: str, default: Any, type_check=False, type_expect=Any):
        self._params[name] = Param.default(
            name,
            default,
            type_check=type_check,
            type_expect=type_expect,
        )
        return self

    def kwargs(self, **kwargs) -> Self:
        self._params.update(
            {name: Param.default(name, default) for name, default in kwargs}
        )
        return self

    def build(self) -> FunctionOpsBuilder:
        return FunctionOpsBuilder(self._ctx.set_params_rev(self._params))
