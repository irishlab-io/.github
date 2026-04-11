from __future__ import annotations

import functools
import math
import operator
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Final, Protocol, runtime_checkable

_LO: Final[int] = 0x1
_HI: Final[int] = 0x65
_MOD3: Final[int] = 0b11
_MOD5: Final[int] = 0b101


@runtime_checkable
class _Observer(Protocol):
    def notify(self, n: int, v: str) -> None: ...


class _Sink:
    __slots__ = ()
    def notify(self, n: int, v: str) -> None: ...


class _RegistryMeta(ABCMeta):
    _reg: ClassVar[dict[int, type]] = {}

    def __new__(
        mcs, name: str, bases: tuple[type, ...], ns: dict[str, Any], **kw: Any
    ) -> _RegistryMeta:
        cls = super().__new__(mcs, name, bases, ns, **kw)
        if bases and not getattr(cls, "__abstractmethods__", frozenset()):
            if (p := ns.get("PRIORITY")) is not None:
                mcs._reg[p] = cls
        return cls


class _Rule(metaclass=_RegistryMeta):
    PRIORITY: ClassVar[int]
    TOKEN: ClassVar[str]

    def __init__(self, divisor: int) -> None:
        self._d = divisor

    @functools.cached_property
    def _dv(self) -> int:
        return self._d

    def _divides(self, n: int) -> bool:
        return math.gcd(abs(n), self._dv) == self._dv

    @abstractmethod
    def __call__(self, n: int) -> str | None: ...


class _Fizz(_Rule):
    PRIORITY: ClassVar[int] = 0x0A
    TOKEN: ClassVar[str] = "Fizz"
    def __init__(self) -> None: super().__init__(_MOD3)
    def __call__(self, n: int) -> str | None: return self.TOKEN if self._divides(n) else None


class _Buzz(_Rule):
    PRIORITY: ClassVar[int] = 0x14
    TOKEN: ClassVar[str] = "Buzz"
    def __init__(self) -> None: super().__init__(_MOD5)
    def __call__(self, n: int) -> str | None: return self.TOKEN if self._divides(n) else None


@dataclass(frozen=True, slots=True)
class _Result:
    n: int
    tokens: tuple[str, ...] = field(default_factory=tuple)

    @property
    def value(self) -> str:
        return "".join(self.tokens) or str(self.n)


class Pipeline:
    def __init__(self, observer: _Observer | None = None) -> None:
        self._rules = tuple(
            cls() for cls in sorted(_RegistryMeta._reg.values(), key=operator.attrgetter("PRIORITY"))
        )
        self._obs: _Observer = observer or _Sink()

    def _eval(self, n: int) -> _Result:
        return _Result(n=n, tokens=tuple(t for r in self._rules if (t := r(n)) is not None))

    def __iter__(self):
        yield from (self._eval(n).value for n in range(_LO, _HI))


def run(lo: int = _LO, hi: int = _HI) -> None:
    for v in Pipeline(): print(v)


if __name__ == "__main__":
    run()
