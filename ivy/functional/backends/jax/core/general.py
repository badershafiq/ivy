"""
Collection of Jax general functions, wrapped to fit Ivy syntax and signature.
"""

# global
import jax as _jax
import math as _math
import numpy as _onp
import jax.numpy as _jnp
import jaxlib as _jaxlib
from numbers import Number
from operator import mul as _mul
from functools import reduce as _reduce
from jaxlib.xla_extension import Buffer
import multiprocessing as _multiprocessing
from haiku._src.data_structures import FlatMapping

# local
from ivy.functional.ivy.core import default_device, default_dtype
from ivy.functional.backends.jax.core.device import to_dev, dev as callable_dev

DTYPE_TO_STR = {_jnp.dtype('int8'): 'int8',
                _jnp.dtype('int16'): 'int16',
                _jnp.dtype('int32'): 'int32',
                _jnp.dtype('int64'): 'int64',
                _jnp.dtype('uint8'): 'uint8',
                _jnp.dtype('uint16'): 'uint16',
                _jnp.dtype('uint32'): 'uint32',
                _jnp.dtype('uint64'): 'uint64',
                _jnp.dtype('bfloat16'): 'bfloat16',
                _jnp.dtype('float16'): 'float16',
                _jnp.dtype('float32'): 'float32',
                _jnp.dtype('float64'): 'float64',
                _jnp.dtype('bool'): 'bool',

                _jnp.int8: 'int8',
                _jnp.int16: 'int16',
                _jnp.int32: 'int32',
                _jnp.int64: 'int64',
                _jnp.uint8: 'uint8',
                _jnp.uint16: 'uint16',
                _jnp.uint32: 'uint32',
                _jnp.uint64: 'uint64',
                _jnp.bfloat16: 'bfloat16',
                _jnp.float16: 'float16',
                _jnp.float32: 'float32',
                _jnp.float64: 'float64',
                _jnp.bool_: 'bool'}

DTYPE_FROM_STR = {'int8': _jnp.dtype('int8'),
                'int16': _jnp.dtype('int16'),
                'int32': _jnp.dtype('int32'),
                'int64': _jnp.dtype('int64'),
                'uint8': _jnp.dtype('uint8'),
                'uint16': _jnp.dtype('uint16'),
                'uint32': _jnp.dtype('uint32'),
                'uint64': _jnp.dtype('uint64'),
                'bfloat16': _jnp.dtype('bfloat16'),
                'float16': _jnp.dtype('float16'),
                'float32': _jnp.dtype('float32'),
                'float64': _jnp.dtype('float64'),
                'bool': _jnp.dtype('bool')}


# Helpers #
# --------#

def _flat_array_to_1_dim_array(x):
    return x.reshape((1,)) if x.shape == () else x


def _to_array(x):
    if isinstance(x, _jax.interpreters.ad.JVPTracer):
        return _to_array(x.primal)
    elif isinstance(x, _jax.interpreters.partial_eval.DynamicJaxprTracer):
        return _to_array(x.aval)
    return x


# API #
# ----#

# noinspection PyShadowingNames
def array(object_in, dtype=None, dev=None):
    if dtype:
        if dtype == 'bool':
            dtype += '_'
        dtype = _jnp.__dict__[dtype]
    else:
        dtype = None
    return to_dev(_jnp.array(object_in, dtype=dtype), default_device(dev))


asarray = array


# noinspection PyUnresolvedReferences,PyProtectedMember
def is_array(x, exclusive=False):
    if exclusive:
        return isinstance(x, (_jax.interpreters.xla._DeviceArray,
                              _jaxlib.xla_extension.DeviceArray, Buffer))
    return isinstance(x, (_jax.interpreters.xla._DeviceArray,
                          _jaxlib.xla_extension.DeviceArray, Buffer,
                          _jax.interpreters.ad.JVPTracer,
                          _jax.core.ShapedArray,
                          _jax.interpreters.partial_eval.DynamicJaxprTracer))


copy_array = _jnp.array
array_equal = _jnp.array_equal
to_numpy = lambda x: _onp.asarray(_to_array(x))
to_numpy.__name__ = 'to_numpy'
to_scalar = lambda x: x if isinstance(x, Number) else _to_array(x).item()
to_scalar.__name__ = 'to_scalar'
to_list = lambda x: _to_array(x).tolist()
to_list.__name__ = 'to_list'
shape = lambda x, as_tensor=False: _jnp.asarray(_jnp.shape(x)) if as_tensor else x.shape
shape.__name__ = 'shape'
get_num_dims = lambda x, as_tensor=False: _jnp.asarray(len(_jnp.shape(x))) if as_tensor else len(x.shape)
minimum = _jnp.minimum
maximum = _jnp.maximum
clip = _jnp.clip
# noinspection PyShadowingBuiltins
round = _jnp.round
floormod = lambda x, y: x % y
floor = _jnp.floor
ceil = _jnp.ceil
# noinspection PyShadowingBuiltins
abs = _jnp.absolute


def argmax(x, axis=0):
    ret = _jnp.argmax(x, axis)
    if ret.shape == ():
        return ret.reshape(-1)
    return ret


def argmin(x, axis=0):
    ret = _jnp.argmin(x, axis)
    if ret.shape == ():
        return ret.reshape(-1)
    return ret


argsort = lambda x, axis=-1: _jnp.argsort(x, axis)


def cast(x, dtype):
    return x.astype(dtype_from_str(dtype))


# noinspection PyShadowingNames
def arange(stop, start=0, step=1, dtype=None, dev=None):
    dtype = dtype_from_str(dtype)
    return to_dev(_jnp.arange(start, stop, step=step, dtype=dtype), default_device(dev))


def linspace(start, stop, num, axis=None, dev=None):
    if axis is None:
        axis = -1
    return to_dev(_jnp.linspace(start, stop, num, axis=axis), default_device(dev))


def logspace(start, stop, num, base=10., axis=None, dev=None):
    if axis is None:
        axis = -1
    return to_dev(_jnp.logspace(start, stop, num, base=base, axis=axis), default_device(dev))


def concatenate(xs, axis=-1):
    if xs[0].shape == ():
        return _jnp.concatenate([_jnp.expand_dims(x, 0) for x in xs], axis)
    return _jnp.concatenate(xs, axis)


def flip(x, axis=None, batch_shape=None):
    num_dims = len(batch_shape) if batch_shape is not None else len(x.shape)
    if not num_dims:
        return x
    if isinstance(axis, list) or isinstance(axis, tuple):
        if len(axis) == 1:
            axis = axis[0]
        else:
            raise Exception('Jax does not support flip() across multiple indices')
    return _jnp.flip(x, axis)


stack = _jnp.stack


def unstack(x, axis, keepdims=False):
    if x.shape == ():
        return [x]
    dim_size = x.shape[axis]
    # ToDo: make this faster somehow, jnp.split is VERY slow for large dim_size
    x_split = _jnp.split(x, dim_size, axis)
    if keepdims:
        return x_split
    return [_jnp.squeeze(item, axis) for item in x_split]


def split(x, num_or_size_splits=None, axis=0, with_remainder=False):
    if x.shape == ():
        if num_or_size_splits is not None and num_or_size_splits != 1:
            raise Exception('input array had no shape, but num_sections specified was {}'.format(num_or_size_splits))
        return [x]
    if num_or_size_splits is None:
        num_or_size_splits = x.shape[axis]
    elif isinstance(num_or_size_splits, int) and with_remainder:
        num_chunks = x.shape[axis] / num_or_size_splits
        num_chunks_int = _math.floor(num_chunks)
        remainder = num_chunks - num_chunks_int
        if remainder != 0:
            num_or_size_splits = [num_or_size_splits]*num_chunks_int + [int(remainder*num_or_size_splits)]
    if isinstance(num_or_size_splits, (list, tuple)):
        num_or_size_splits = _jnp.cumsum(_jnp.array(num_or_size_splits[:-1]))
    return _jnp.split(x, num_or_size_splits, axis)


repeat = _jnp.repeat
tile = _jnp.tile
constant_pad = lambda x, pad_width, value=0: _jnp.pad(_flat_array_to_1_dim_array(x), pad_width, constant_values=value)
zero_pad = lambda x, pad_width: _jnp.pad(_flat_array_to_1_dim_array(x), pad_width, constant_values=0)
swapaxes = _jnp.swapaxes


def transpose(x, axes=None):
    if axes is None:
        num_dims = len(x.shape)
        axes = list(range(num_dims))
        axes.reverse()
    return _jnp.transpose(x, axes)


expand_dims = _jnp.expand_dims
where = lambda condition, x1, x2: _jnp.where(condition, x1, x2)


def indices_where(x):
    where_x = _jnp.where(x)
    ret = _jnp.concatenate([_jnp.expand_dims(item, -1) for item in where_x], -1)
    return ret


isnan = _jnp.isnan
isinf = _jnp.isinf

def isfinite(x):
    return _jnp.isfinite(x)

def floor(x):
    return _jnp.floor(x)

reshape = _jnp.reshape
broadcast_to = _jnp.broadcast_to


def squeeze(x, axis=None):
    if x.shape == ():
        if axis is None or axis == 0 or axis == -1:
            return x
        raise Exception('tried to squeeze a zero-dimensional input by axis {}'.format(axis))
    return _jnp.squeeze(x, axis)


# noinspection PyShadowingNames
def zeros(shape, dtype='float32', dev=None):
    dtype = _jnp.__dict__[dtype]
    return to_dev(_jnp.zeros(shape, dtype), default_device(dev))


# noinspection PyShadowingNames
def zeros_like(x, dtype=None, dev=None):
    if dtype:
        dtype = _jnp.__dict__[dtype]
    else:
        dtype = x.dtype
    return to_dev(_jnp.zeros_like(x, dtype=dtype), default_device(dev))


def full(shape, fill_value, dtype=None, device=None):
    return to_dev(_jnp.full(shape, fill_value, dtype_from_str(default_dtype(dtype, fill_value))), default_device(device))


# noinspection PyShadowingNames
def ones(shape, dtype=None, dev=None):
    return to_dev(_jnp.ones(shape, dtype_from_str(default_dtype(dtype))), default_device(dev))


# noinspection PyShadowingNames
def ones_like(x, dtype=None, dev=None):
    if dtype:
        dtype = _jnp.__dict__[dtype]
    else:
        dtype = x.dtype
    return to_dev(_jnp.ones_like(x, dtype=dtype), default_device(dev))


# noinspection PyUnusedLocal
def one_hot(indices, depth, dev=None):
    # from https://stackoverflow.com/questions/38592324/one-hot-encoding-using-numpy
    res = _jnp.eye(depth)[_jnp.array(indices).reshape(-1)]
    return to_dev(res.reshape(list(indices.shape) + [depth]), default_device(dev))


cross = _jnp.cross
matmul = lambda x1, x2: _jnp.matmul(x1, x2)
cumsum = _jnp.cumsum


def cumprod(x, axis=0, exclusive=False):
    if exclusive:
        x = _jnp.swapaxes(x, axis, -1)
        x = _jnp.concatenate((_jnp.ones_like(x[..., -1:]), x[..., :-1]), -1)
        res = _jnp.cumprod(x, -1)
        return _jnp.swapaxes(res, axis, -1)
    return _jnp.cumprod(x, axis)


# noinspection PyShadowingNames
def identity(n, dtype='float32', batch_shape=None, dev=None):
    dtype = _jnp.__dict__[dtype]
    mat = _jnp.identity(n, dtype=dtype)
    if batch_shape is None:
        return_mat = mat
    else:
        reshape_dims = [1]*len(batch_shape) + [n, n]
        tile_dims = list(batch_shape) + [1, 1]
        return_mat = _jnp.tile(_jnp.reshape(mat, reshape_dims), tile_dims)
    return to_dev(return_mat, default_device(dev))


meshgrid = lambda *xs, indexing='ij': _jnp.meshgrid(*xs, indexing=indexing)


def scatter_flat(indices, updates, size, reduction='sum', dev=None):
    if dev is None:
        dev = callable_dev(updates)
    if reduction == 'sum':
        target = _jnp.zeros([size], dtype=updates.dtype)
        target = target.at[indices].add(updates)
    elif reduction == 'min':
        target = _jnp.ones([size], dtype=updates.dtype)*1e12
        target = target.at[indices].min(updates)
        target = _jnp.where(target == 1e12, 0., target)
    elif reduction == 'max':
        target = _jnp.ones([size], dtype=updates.dtype)*-1e12
        target = target.at[indices].max(updates)
        target = _jnp.where(target == -1e12, 0., target)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    return to_dev(target, dev)


# noinspection PyShadowingNames
def scatter_nd(indices, updates, shape, reduction='sum', dev=None):
    if dev is None:
        dev = callable_dev(updates)
    shape = list(shape)
    indices_flat = indices.reshape(-1, indices.shape[-1]).T
    indices_tuple = tuple(indices_flat) + (Ellipsis,)
    if reduction == 'sum':
        target = _jnp.zeros(shape, dtype=updates.dtype)
        target = target.at[indices_tuple].add(updates)
    elif reduction == 'min':
        target = _jnp.ones(shape, dtype=updates.dtype)*1e12
        target = target.at[indices_tuple].min(updates)
        target = _jnp.where(target == 1e12, 0., target)
    elif reduction == 'max':
        target = _jnp.ones(shape, dtype=updates.dtype)*-1e12
        target = target.at[indices_tuple].max(updates)
        target = _jnp.where(target == -1e12, 0., target)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    return to_dev(target, dev)


def gather(params, indices, axis=-1, dev=None):
    if dev is None:
        dev = callable_dev(params)
    return to_dev(_jnp.take_along_axis(params, indices, axis), dev)


def gather_nd(params, indices, dev=None):
    if dev is None:
        dev = callable_dev(params)
    indices_shape = indices.shape
    params_shape = params.shape
    num_index_dims = indices_shape[-1]
    res_dim_sizes_list = [_reduce(_mul, params_shape[i + 1:], 1) for i in range(len(params_shape) - 1)] + [1]
    result_dim_sizes = _jnp.array(res_dim_sizes_list)
    implicit_indices_factor = int(result_dim_sizes[num_index_dims - 1].item())
    flat_params = _jnp.reshape(params, (-1,))
    new_shape = [1] * (len(indices_shape) - 1) + [num_index_dims]
    indices_scales = _jnp.reshape(result_dim_sizes[0:num_index_dims], new_shape)
    indices_for_flat_tiled = _jnp.tile(_jnp.reshape(_jnp.sum(indices * indices_scales, -1, keepdims=True), (-1, 1)), (1, implicit_indices_factor))
    implicit_indices = _jnp.tile(_jnp.expand_dims(_jnp.arange(implicit_indices_factor), 0), (indices_for_flat_tiled.shape[0], 1))
    indices_for_flat = indices_for_flat_tiled + implicit_indices
    flat_indices_for_flat = _jnp.reshape(indices_for_flat, (-1,)).astype(_jnp.int32)
    flat_gather = _jnp.take(flat_params, flat_indices_for_flat, 0)
    new_shape = list(indices_shape[:-1]) + list(params_shape[num_index_dims:])
    ret = _jnp.reshape(flat_gather, new_shape)
    return to_dev(ret, dev)


def linear_resample(x, num_samples, axis=-1):
    x_shape = list(x.shape)
    num_x_dims = len(x_shape)
    axis = axis % num_x_dims
    x_pre_shape = x_shape[0:axis]
    x_pre_size = _reduce(_mul, x_pre_shape) if x_pre_shape else 1
    num_pre_dims = len(x_pre_shape)
    num_vals = x.shape[axis]
    x_post_shape = x_shape[axis+1:]
    x_post_size = _reduce(_mul, x_post_shape) if x_post_shape else 1
    num_post_dims = len(x_post_shape)
    xp = _jnp.reshape(_jnp.arange(num_vals*x_pre_size*x_post_size), x_shape)
    x_coords = _jnp.arange(num_samples) * ((num_vals-1)/(num_samples-1)) * x_post_size
    x_coords = _jnp.reshape(x_coords, [1]*num_pre_dims + [num_samples] + [1]*num_post_dims)
    x_coords = _jnp.broadcast_to(x_coords, x_pre_shape + [num_samples] + x_post_shape)
    slc = [slice(None)] * num_x_dims
    slc[axis] = slice(0, 1, 1)
    x_coords = x_coords + xp[tuple(slc)]
    x = _jnp.reshape(x, (-1,))
    xp = _jnp.reshape(xp, (-1,))
    x_coords = _jnp.reshape(x_coords, (-1,))
    ret = _jnp.interp(x_coords, xp, x)
    return _jnp.reshape(ret, x_pre_shape + [num_samples] + x_post_shape)


def dtype(x, as_str=False):
    dt = x.dtype
    if as_str:
        return dtype_to_str(dt)
    return dt


def dtype_to_str(dtype_in):
    if isinstance(dtype_in, str):
        return dtype_in
    return DTYPE_TO_STR[dtype_in]


def dtype_from_str(dtype_in):
    if not isinstance(dtype_in, str):
        return dtype_in
    return DTYPE_FROM_STR[dtype_in]


compile = lambda fn, dynamic=True, example_inputs=None, static_argnums=None, static_argnames=None:\
    _jax.jit(fn, static_argnums=static_argnums, static_argnames=static_argnames)
current_framework_str = lambda: 'jax'
current_framework_str.__name__ = 'current_framework_str'
multiprocessing = lambda context=None: _multiprocessing if context is None else _multiprocessing.get_context(context)
container_types = lambda: [FlatMapping]


def inplace_update(x, val):
    raise Exception('Jax does not support inplace operations')


def inplace_decrement(x, val):
    raise Exception('Jax does not support inplace operations')


def inplace_increment(x, val):
    raise Exception('Jax does not support inplace operations')


inplace_arrays_supported = lambda: False
inplace_variables_supported = lambda: False
