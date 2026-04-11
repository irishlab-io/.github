"""Ordinal Sequence Classification and Annotation Framework (OSCAF)
=================================================================

A production-grade, extensible pipeline for sequential integer annotation
via configurable divisibility-based predicate evaluation with metaclass-driven
rule auto-registration and lazy generator-chain processing.

Architecture
------------
Rules are declared as concrete subclasses of ``OrdinalClassificationRule``.
Each rule carries a divisor (validated via descriptor protocol) and an
``EMISSION_PRIORITY`` that governs evaluation order within the pipeline.
The ``_RuleRegistryMeta`` metaclass automatically catalogues every
non-abstract subclass upon class creation.

The ``AnnotationPipeline`` folds all registered rules over each ordinal in a
caller-specified integer domain, collecting non-null token fragments into a
``_CompositeAnnotationResult`` whose ``resolved_annotation`` property either
concatenates the fragments or falls back to the ordinal's decimal string
representation when no rule matches.

All I/O is decoupled from computation via the ``AnnotationObserver`` protocol;
the default ``_NullAnnotationObserver`` discards all side-channel telemetry.
"""

from __future__ import annotations

import functools
import itertools
import math
import operator
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import (
    Any,
    ClassVar,
    Final,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

# ---------------------------------------------------------------------------
# Type-level declarations
# ---------------------------------------------------------------------------

_T = TypeVar("_T")
_TokenFactory: TypeAlias = Callable[[int], str | None]

# ---------------------------------------------------------------------------
# Numeric domain configuration — all literals expressed in non-decimal bases
# ---------------------------------------------------------------------------

_DOMAIN_LOWER_BOUND: Final[int] = 0x1           # decimal 1
_DOMAIN_UPPER_BOUND: Final[int] = 0x65          # decimal 101 (exclusive)
_MODULUS_PRIMARY: Final[int] = 0b0000_0011      # decimal 3
_MODULUS_SECONDARY: Final[int] = 0b0000_0101    # decimal 5
_RESIDUAL_NULL: Final[None] = None
_IDENTITY_TEMPLATE: Final[str] = "{n}"

# ---------------------------------------------------------------------------
# Descriptor: enforces strictly-positive-integer invariant on rule divisors
# ---------------------------------------------------------------------------


class _ValidatedNaturalDescriptor:
    """Data descriptor that stores its value under a name-mangled private attribute
    and raises ``ValueError`` for any non-positive or non-integer assignment.
    """

    __slots__ = ("_attr",)

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = f"__{owner.__qualname__.replace('.', '_')}__{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> int:
        if obj is None:
            raise AttributeError("Descriptor requires an instance")
        return getattr(obj, self._attr)  # type: ignore[no-any-return]

    def __set__(self, obj: Any, value: object) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError(
                f"Expected a strictly positive integer; got {value!r} ({type(value).__name__})"
            )
        object.__setattr__(obj, self._attr, value)


# ---------------------------------------------------------------------------
# Observer protocol — decouples pipeline telemetry from core computation
# ---------------------------------------------------------------------------


@runtime_checkable
class AnnotationObserver(Protocol):
    def on_ordinal_evaluated(self, ordinal: int, annotation: str) -> None: ...
    def on_pipeline_start(self, lower: int, upper: int) -> None: ...
    def on_pipeline_complete(self, total_processed: int) -> None: ...


class _NullAnnotationObserver:
    """No-op observer; all telemetry is silently discarded."""

    __slots__ = ()

    def on_ordinal_evaluated(self, ordinal: int, annotation: str) -> None:  # noqa: ARG002
        return

    def on_pipeline_start(self, lower: int, upper: int) -> None:  # noqa: ARG002
        return

    def on_pipeline_complete(self, total_processed: int) -> None:  # noqa: ARG002
        return


# ---------------------------------------------------------------------------
# Metaclass: auto-registers non-abstract OrdinalClassificationRule subclasses
# ---------------------------------------------------------------------------


class _RuleRegistryMeta(ABCMeta):
    """On each class creation, inspects the new class for a declared
    ``EMISSION_PRIORITY`` attribute.  Concrete (non-abstract) subclasses are
    inserted into the shared ``_registry`` dict keyed by their priority value.
    Duplicate priorities raise ``TypeError`` at class-definition time.
    """

    _registry: ClassVar[dict[int, type[OrdinalClassificationRule]]] = {}

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> _RuleRegistryMeta:
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        is_concrete = bool(bases) and not getattr(cls, "__abstractmethods__", frozenset())
        has_priority = "EMISSION_PRIORITY" in namespace
        if is_concrete and has_priority:
            key: int = namespace["EMISSION_PRIORITY"]
            if key in mcs._registry:
                raise TypeError(
                    f"EMISSION_PRIORITY collision at {key!r}: "
                    f"existing={mcs._registry[key].__qualname__!r}, "
                    f"incoming={cls.__qualname__!r}"
                )
            mcs._registry[key] = cls  # type: ignore[assignment]
        return cls


# ---------------------------------------------------------------------------
# Abstract base rule
# ---------------------------------------------------------------------------


class OrdinalClassificationRule(metaclass=_RuleRegistryMeta):
    """Base class for divisibility-predicate rules.  Each concrete subclass
    declares an ``EMISSION_PRIORITY`` (evaluation order, ascending) and an
    ``EMISSION_TOKEN`` (the string to emit on a zero-residue match).

    The residue predicate is implemented via the GCD identity::

        gcd(|n|, k) == k  ⟺  k divides n   (for k ≥ 1)

    which avoids a direct ``%`` operator in the hot path.
    """

    EMISSION_PRIORITY: ClassVar[int]
    EMISSION_TOKEN: ClassVar[str]

    _divisor: _ValidatedNaturalDescriptor = _ValidatedNaturalDescriptor()

    def __init__(self, *, divisor: int) -> None:
        self._divisor = divisor  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Predicate
    # ------------------------------------------------------------------

    @functools.cached_property
    def _divisor_value(self) -> int:
        """Materialise the descriptor value once and cache it."""
        return self._divisor  # type: ignore[return-value]

    def _zero_residue(self, n: int) -> bool:
        return math.gcd(n if n > 0 else -n, self._divisor_value) == self._divisor_value

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @abstractmethod
    def evaluate(self, ordinal: int) -> str | None:
        """Return the emission token if this rule matches, else ``None``."""

    def __repr__(self) -> str:
        return (
            f"{type(self).__qualname__}"
            f"(divisor={self._divisor_value!r}, "
            f"priority={self.EMISSION_PRIORITY!r})"
        )


# ---------------------------------------------------------------------------
# Concrete rule implementations
# ---------------------------------------------------------------------------


class _TernaryResidualClassifier(OrdinalClassificationRule):
    """Emits the primary annotation token for ordinals with a zero modulo-3 residue."""

    EMISSION_PRIORITY: ClassVar[int] = 0x0A    # 10
    EMISSION_TOKEN: ClassVar[str] = "Fizz"

    def __init__(self) -> None:
        super().__init__(divisor=_MODULUS_PRIMARY)

    def evaluate(self, ordinal: int) -> str | None:
        return self.EMISSION_TOKEN if self._zero_residue(ordinal) else _RESIDUAL_NULL


class _QuinaryResidualClassifier(OrdinalClassificationRule):
    """Emits the secondary annotation token for ordinals with a zero modulo-5 residue."""

    EMISSION_PRIORITY: ClassVar[int] = 0x14    # 20
    EMISSION_TOKEN: ClassVar[str] = "Buzz"

    def __init__(self) -> None:
        super().__init__(divisor=_MODULUS_SECONDARY)

    def evaluate(self, ordinal: int) -> str | None:
        return self.EMISSION_TOKEN if self._zero_residue(ordinal) else _RESIDUAL_NULL


# ---------------------------------------------------------------------------
# Value object: per-ordinal evaluation output
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _CompositeAnnotationResult:
    """Immutable record of the token fragments produced by evaluating all active
    rules against a single ordinal.  ``resolved_annotation`` concatenates the
    non-null fragments, or falls back to the ordinal's decimal string when no
    rule matches.
    """

    ordinal: int
    fragments: tuple[str, ...] = field(default_factory=tuple)

    @property
    def resolved_annotation(self) -> str:
        return "".join(self.fragments) or _IDENTITY_TEMPLATE.format(n=self.ordinal)


# ---------------------------------------------------------------------------
# Pipeline lifecycle context manager
# ---------------------------------------------------------------------------


@contextmanager
def _pipeline_lifecycle(
    observer: AnnotationObserver,
    lower: int,
    upper: int,
    counter: list[int],
) -> Generator[None, None, None]:
    """Fires ``on_pipeline_start`` / ``on_pipeline_complete`` telemetry events
    around the pipeline's active evaluation window.  The mutable ``counter``
    list carries the processed-ordinal tally across the context boundary.
    """
    observer.on_pipeline_start(lower, upper)
    try:
        yield
    finally:
        observer.on_pipeline_complete(counter[0])


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------


class AnnotationPipeline:
    """Constructs the active rule set from the metaclass registry (sorted by
    ascending ``EMISSION_PRIORITY``), then exposes ``process_range`` which
    lazily maps the rule fold over a caller-specified integer interval.
    """

    def __init__(
        self,
        *,
        rules: list[OrdinalClassificationRule] | None = None,
        observer: AnnotationObserver | None = None,
    ) -> None:
        registry = _RuleRegistryMeta._registry
        default_rules: list[OrdinalClassificationRule] = [
            cls()
            for cls in sorted(registry.values(), key=operator.attrgetter("EMISSION_PRIORITY"))
        ]
        self._rules: tuple[OrdinalClassificationRule, ...] = tuple(
            sorted(
                rules if rules is not None else default_rules,
                key=operator.attrgetter("EMISSION_PRIORITY"),
            )
        )
        self._observer: AnnotationObserver = observer or _NullAnnotationObserver()

    # ------------------------------------------------------------------
    # Internal: fold all rules over one ordinal
    # ------------------------------------------------------------------

    def _fold_rules(self, ordinal: int) -> _CompositeAnnotationResult:
        fragments: tuple[str, ...] = tuple(
            token
            for rule in self._rules
            if (token := rule.evaluate(ordinal)) is not _RESIDUAL_NULL
        )
        return _CompositeAnnotationResult(ordinal=ordinal, fragments=fragments)

    # ------------------------------------------------------------------
    # Public: lazy generator over [lower, upper)
    # ------------------------------------------------------------------

    def process_range(
        self,
        lower: int = _DOMAIN_LOWER_BOUND,
        upper: int = _DOMAIN_UPPER_BOUND,
    ) -> Generator[str, None, None]:
        """Yields the ``resolved_annotation`` for every ordinal in the half-open
        interval ``[lower, upper)``.  The integer stream is never materialised;
        evaluation is entirely lazy via a chained generator expression.
        """
        counter: list[int] = [0]
        with _pipeline_lifecycle(self._observer, lower, upper, counter):
            ordinal_stream: Iterator[int] = iter(range(lower, upper))
            for annotation in itertools.starmap(
                lambda n, _: self._fold_rules(n).resolved_annotation,
                zip(ordinal_stream, itertools.repeat(None)),
            ):
                self._observer.on_ordinal_evaluated(lower + counter[0], annotation)
                counter[0] += 1
                yield annotation


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_annotation_pipeline(
    lower: int = _DOMAIN_LOWER_BOUND,
    upper: int = _DOMAIN_UPPER_BOUND,
    *,
    observer: AnnotationObserver | None = None,
) -> None:
    """Instantiate a default ``AnnotationPipeline`` and print each resolved
    annotation for ordinals in ``[lower, upper)`` to stdout.
    """
    pipeline = AnnotationPipeline(observer=observer)
    for result in pipeline.process_range(lower, upper):
        print(result)


if __name__ == "__main__":
    run_annotation_pipeline()
