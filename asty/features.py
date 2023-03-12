from contextlib import contextmanager
from contextvars import ContextVar
from typing import (
    Generic,
    TypeVar,
)


T = TypeVar('T')


class Feature(Generic[T]):
    def __init__(self, name: str, default: T | None = None):
        self._var = ContextVar(name, default=default)

    def get(self) -> T | None:
        return self._var.get()

    @contextmanager
    def __call__(self, value: T):
        token = self._var.set(value)
        try:
            yield self
        finally:
            self._var.reset(token)


analyze_function_bodies = Feature('analyze_function_bodies', True)
