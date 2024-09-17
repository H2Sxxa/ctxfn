from enum import Enum
from typing import Any, Callable, List, Optional, Self
from ctxfn.context import FunctionContext
from ctxfn.types import P, T


class ContextDirective:
    class Directive(Enum):
        RETURN = 0
        CONTINUE = 1

    context: FunctionContext
    directive: Directive
    directive_message: Any

    def __init__(self, context: FunctionContext[Any], next=True, message=None) -> None:
        self.context = context
        self.directive = (
            ContextDirective.Directive.CONTINUE
            if next
            else ContextDirective.Directive.RETURN
        )

        self.directive_message = message


class ConditionBuilder:
    pass


class ExpressionBuilder:
    pass


class FunctionOpsBuilder:
    _current: Any
    _ctx: FunctionContext[Self]
    _ops: List[Callable[[FunctionContext], ContextDirective]]

    def __init__(self, context: FunctionContext[Any]) -> None:
        self._ctx = context.set_backto_mut(self)
        self._ops = []

    def _ensure_context_directive(
        self,
        result: Any,
        context: FunctionContext[Any],
        next=True,
        message=None,
    ) -> ContextDirective:
        return ContextDirective(
            result if result is FunctionContext else context, next, message
        )

    def context(self, factory: Callable[[FunctionContext], Optional[FunctionContext]]):
        self._ops.append(
            lambda context: self._ensure_context_directive(factory(context), context)
        )
        return self

    def expression(self) -> ExpressionBuilder:
        pass

    def condition(self) -> ConditionBuilder:
        pass

    def call(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        self._ops.append(
            lambda context: self._ensure_context_directive(
                func(*args, **kwargs), context
            )
        )
        return self

    def call_context(
        self,
        func: Callable[P, T],
        caller: Callable[[FunctionContext, Callable[P, T]], Optional[FunctionContext]],
    ) -> Self:
        self._ops.append(
            lambda context: self._ensure_context_directive(
                caller(context, func), context
            )
        )
        return self

    def return_current(self) -> Self:
        self._ops.append(lambda ctx: ContextDirective(ctx, False, ctx.current))
        return self

    def return_local(self, name: str) -> Self:
        self._ops.append(
            lambda ctx: ContextDirective(ctx, False, ctx.locals_vars[name])
        )
        return self

    def return_value(self, value=None) -> Self:
        self._ops.append(lambda ctx: ContextDirective(ctx, False, value))
        return self

    def build(self) -> Callable:
        def real(*args, **kwargs):
            assert self._ctx._params_rev is not None
            self._ctx._params_rev(*args, **kwargs)
            for op in self._ops:
                ctxd = op(self._ctx)
                self._ctx = ctxd.context
                if ctxd.directive == ContextDirective.Directive.RETURN:
                    return ctxd.directive_message

        return real
