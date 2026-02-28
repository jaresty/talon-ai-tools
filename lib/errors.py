"""
Structured error hierarchy for talon-ai-tools.

All domain errors extend TalonAIError so callers can catch the broad base
or a specific subclass depending on how much granularity they need.
"""

from functools import wraps
from typing import Type


class TalonAIError(Exception):
    """Base exception for all talon-ai-tools errors."""


class StateError(TalonAIError):
    """Raised when GPTState is accessed or mutated in an invalid way."""


class ConfigError(TalonAIError):
    """Raised when configuration is missing, invalid, or has conflicting precedence."""


class ProviderError(TalonAIError):
    """Raised when an AI provider fails, is misconfigured, or lacks a capability."""


def error_context(label: str, error_class: Type[TalonAIError] = TalonAIError):
    """Decorator that catches bare exceptions and re-raises as TalonAIError subclasses.

    Usage:
        @error_context("loading config", error_class=ConfigError)
        def load():
            ...

    Any exception raised inside the decorated function is wrapped in `error_class`
    with `label` prepended to the message. The original exception is chained as
    __cause__ so tracebacks remain readable.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except TalonAIError:
                raise
            except Exception as exc:
                raise error_class(f"{label}: {exc}") from exc
        return wrapper
    return decorator
