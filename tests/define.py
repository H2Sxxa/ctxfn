from ctxfn.expression.define import DefineBuilder

# Just about 25 times slower than native...lol
add = (
    DefineBuilder()
    .arg("a")
    .arg("b")
    .build()
    .context(
        lambda context: context.set_current(
            context.locals_vars["a"] + context.locals_vars["b"]
        )
    )
    .call_context(print, lambda context, func: func(context.get_current()))
    .return_current()
    .build()
)

add(1, 2)
