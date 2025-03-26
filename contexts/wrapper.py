from contextvars import ContextVar
from typing import Generic, TypeVar

T = TypeVar("T")


class HiddenValue:
    pass


_default = HiddenValue()


class RecyclableContextVar(Generic[T]):
    """
    RecyclableContextVar is a wrapper around ContextVar
    It's safe to use in gunicorn with thread recycling, but features like `reset` are not available for now

    NOTE: you need to call `increment_thread_recycles` before requests

    基于 Python 标准库中的 ContextVar，用于在多线程、线程回收的场景下，管理上下文变量的状态和版本控制。
    """

    _thread_recycles: ContextVar[int] = ContextVar("thread_recycles")

    @classmethod
    def increment_thread_recycles(cls):
        """
        增量更新方法：
        :return:  回收次数
        """
        try:
            recycles = cls._thread_recycles.get()
            cls._thread_recycles.set(recycles + 1)
        except LookupError:
            cls._thread_recycles.set(0)

    def __init__(self, context_var: ContextVar[T]):
        """
        更新计数器
        :param context_var:
        """
        self._context_var = context_var
        self._updates = ContextVar[int](context_var.name + "_updates", default=0)

    def get(self, default: T | HiddenValue = _default) -> T:
        """
        首先获取全局的线程回收次数和当前实例的更新计数器。
        如果全局回收次数大于实例更新计数器，说明当前上下文已经“过期”，需要更新计数器。
        如果实例更新计数器依然落后（或相等）于全局回收次数，说明当前值可能已失效，则根据是否提供默认值决定抛出异常或返回默认值。

        """
        thread_recycles = self._thread_recycles.get(0)
        self_updates = self._updates.get()
        if thread_recycles > self_updates:
            self._updates.set(thread_recycles)

        # check if thread is recycled and should be updated
        if thread_recycles < self_updates:
            return self._context_var.get()
        else:
            # thread_recycles >= self_updates, means current context is invalid
            if isinstance(default, HiddenValue) or default is _default:
                raise LookupError
            else:
                return default

    def set(self, value: T):
        """
        同样先对比全局回收次数和实例的更新计数器，保持它们同步。
        如果二者相等，手动增加实例的更新计数器（相当于标记值已更新）。
        最后将新值设置到包装的原始 ContextVar 中。
        :param value:
        :return:
        """
        # it leads to a situation that self.updates is less than cls.thread_recycles if `set` was never called before
        # increase it manually
        thread_recycles = self._thread_recycles.get(0)
        self_updates = self._updates.get()
        if thread_recycles > self_updates:
            self._updates.set(thread_recycles)

        if self._updates.get() == self._thread_recycles.get(0):
            # after increment,
            self._updates.set(self._updates.get() + 1)

        # set the context
        self._context_var.set(value)
