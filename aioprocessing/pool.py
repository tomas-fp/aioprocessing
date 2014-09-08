from multiprocessing import Pool
from asyncio import Future
import asyncio

from .executor import CoroBuilder

__all__ = ['AioPool']

class AioPool(metaclass=CoroBuilder):
    delegate = Pool
    coroutines = ['join']

    def _coro_func(self, funcname, *args, **kwargs):
        """ Call the given function, and wrap the reuslt in a Future. 
        
        funcname should be the name of a function which takes `callback` 
        and `error_callback` keyword arguments (e.g. apply_async).
        
        """
        loop = asyncio.get_event_loop()
        fut = Future()
        def set_result(result):
            loop.call_soon_threadsafe(fut.set_result, result)
        def set_exc(exc):
            loop.call_soon_threadsafe(fut.set_exception, exc)

        func = getattr(self._obj, funcname)
        func(*args, callback=set_result, 
             error_callback=set_exc, **kwargs)
        return fut

    def coro_apply(self, func, args=(), kwds={}):
        return self._coro_func('apply_async', func, 
                               args=args, kwds=kwds)

    def coro_map(self, func, iterable, chunksize=None):
        return self._coro_func('map_async', func, iterable, 
                               chunksize=chunksize)

    def coro_starmap(self, func, iterable, chunksize=None):
        return self._coro_func('starmap_async', func, iterable, 
                               chunksize=chunksize)

    def __enter__(self):
        self._obj.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._obj.__exit__(*args, **kwargs)
