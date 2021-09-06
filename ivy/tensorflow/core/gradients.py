"""
Collection of TensorFlow gradient functions, wrapped to fit Ivy syntax and signature.
"""

# global
import tensorflow as _tf

# local
import ivy
from ivy.core.container import Container


def variable(x):
    with _tf.device('/' + ivy.dev_str(x).upper()):
        return _tf.Variable(x, trainable=True)


def is_variable(x):
    return isinstance(x, _tf.Variable)


def inplace_update(x, val):
    x.assign(val)
    return x


def inplace_decrement(x, val):
    x.assign(x - val)
    return x


def inplace_increment(x, val):
    x.assign(x + val)
    return x


def execute_with_gradients(func, xs, retain_grads=False):
    with _tf.GradientTape(persistent=retain_grads, watch_accessed_variables=False) as tape:
        tape.watch(xs)
        func_ret = func(xs)
    if isinstance(func_ret, tuple):
        y = func_ret[0]
        rest = func_ret[1:]
    else:
        y = func_ret
        rest = tuple()
    grads = Container(tape.gradient(y, xs))
    return (y, grads, *rest)


def stop_gradient(x, preserve_type=True):
    is_var = is_variable(x)
    x = _tf.stop_gradient(x)
    if is_var and preserve_type:
        return variable(x)
    return x
