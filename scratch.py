import jax
import jax.numpy as np
import jax.numpy as jnp
from functools import partial

from jax.gmap import LoopType, gmap_impl

import os
from jax.lib import xla_bridge
os.environ["XLA_FLAGS"] = "--xla_force_host_platform_device_count=8"
# Clear any cached backends so new CPU backend will pick up the env var.
xla_bridge.get_backend.cache_clear()
print(jax.devices())

def f(x, y):
    return x.dot(jnp.sin(y))

lim_vmap = [(LoopType.sequential, None), (LoopType.vectorized, 2)]
vmap = [(LoopType.vectorized, None)]

h = jax.api.gmap(f, schedule=lim_vmap)

x = jnp.ones((8, 64, 64))
print(jax.make_jaxpr(h)(x, x))
h(x, x)

import jax.linear_util as lu
def h(x, y):
  return gmap_impl(lu.wrap_init(lambda x, y: (f(x, y),)),
                   x, y,
                   axis_name='i', axis_size=8,
                   schedule=tuple(lim_vmap),
                   mapped_invars=(True, True))

print(jax.make_jaxpr(h)(x, x))


# z = jax.pmap(f)(x, x)
