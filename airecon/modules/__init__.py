"""
AIRecon module registry and dynamic loader.

This module provides a centralized registry for reconnaissance modules,
a base class for module implementations, and functions to discover,
register, and load modules at runtime.

Usage:
    from airecon.modules import load_module, list_modules, BaseModule

    class MyModule(BaseModule):
        name = "my_module"
        description = "Does something useful"
        async def run(self, target: str, context: dict) -> dict:
            return {"result": "ok"}

    register_module(MyModule)

    mod = load_module("my_module")
    result = await mod.run("example.com", {})
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict, List, Optional, Type

import airecon.modules as modules_package  # top-level package for discovery

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base module class
# ---------------------------------------------------------------------------

class BaseModule:
    """Abstract base for all reconnaissance modules.

    Subclasses **must** set `name` and `description` as class attributes,
    and implement the `run` method.

    Attributes:
        name: Unique identifier for the module (lowercase, underscores).
        description: Human-readable description of what the module does.
    """
    name: str = ""
    description: str = ""

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the reconnaissance module.

        Args:
            target: The target domain, IP, or URI to scan.
            context: Optional dictionary carrying session state or shared data.

        Returns:
            A dictionary containing the results (must be JSON-serializable).

        Raises:
            NotImplementedError: If the subclass does not override this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")


# ---------------------------------------------------------------------------
# Internal registry
# ---------------------------------------------------------------------------

_registry: Dict[str, Type[BaseModule]] = {}


def register_module(module_class: Type[BaseModule], *, force: bool = False) -> None:
    """Register a module class in the global registry.

    Args:
        module_class: A class that inherits from BaseModule.
        force: If True, overwrite an existing registration with the same name.

    Raises:
        ValueError: If the class does not inherit from BaseModule or lacks a name.
        KeyError: If a module with the same name is already registered and force is False.
    """
    if not (isinstance(module_class, type) and issubclass(module_class, BaseModule)):
        raise ValueError(f"{module_class} must be a subclass of BaseModule")

    name = getattr(module_class, "name", None)
    if not name:
        raise ValueError(f"Module class {module_class.__name__} must have a non-empty 'name' attribute")

    if name in _registry and not force:
        raise KeyError(f"Module '{name}' is already registered (use force=True to overwrite)")

    _registry[name] = module_class
    logger.debug("Registered module: %s (%s)", name, module_class.__module__)


def unregister_module(name: str) -> None:
    """Remove a module from the registry.

    Args:
        name: The name of the module to remove.

    Raises:
        KeyError: If the module is not registered.
    """
    if name not in _registry:
        raise KeyError(f"Module '{name}' is not registered")
    del _registry[name]
    logger.debug("Unregistered module: %s", name)


def list_modules() -> List[Dict[str, str]]:
    """Return metadata for all currently registered modules.

    Returns:
        A list of dicts with keys 'name' and 'description'.
    """
    return [
        {"name": name, "description": cls.description or "No description"}
        for name, cls in _registry.items()
    ]


def is_registered(name: str) -> bool:
    """Check if a module is registered."""
    return name in _registry


# ---------------------------------------------------------------------------
# Dynamic loading
# ---------------------------------------------------------------------------

def load_module(name: str) -> Type[BaseModule]:
    """Retrieve a registered module class by name.

    If the module is not yet registered, the function attempts to discover
    and import it from the `airecon.modules` package tree.

    Args:
        name: The name of the module (as set in its `name` attribute).

    Returns:
        The module class (subclass of BaseModule).

    Raises:
        KeyError: If the module cannot be found or loaded.
    """
    if name in _registry:
        return _registry[name]

    # Attempt auto-discovery by scanning all subpackages/modules
    _discover_all()

    if name not in _registry:
        raise KeyError(f"Module '{name}' not found in registry and could not be auto-discovered")

    return _registry[name]


def _discover_all() -> None:
    """Walk through all submodules of `airecon.modules` and trigger registration."""
    # Prevent repeated discovery
    if hasattr(_discover_all, "_done"):
        return
    _discover_all._done = True  # type: ignore

    package = modules_package
    prefix = package.__name__ + "."
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=package.__path__,
        prefix=prefix,
        onerror=lambda name: logger.warning("Failed to walk package %s", name),
    ):
        if ispkg:
            continue
        try:
            # Import the module – its top-level code should call register_module
            importlib.import_module(modname)
        except Exception as exc:
            logger.debug("Could not load module %s: %s", modname, exc)


def get_module_class(name: str) -> Optional[Type[BaseModule]]:
    """Safely retrieve a module class without auto-discovery."""
    return _registry.get(name)


# ---------------------------------------------------------------------------
# Convenience decorator
# ---------------------------------------------------------------------------

def module(name: Optional[str] = None, description: str = ""):
    """Decorator that registers a BaseModule subclass automatically.

    Usage:
        @module(name="my_scan", description="Performs a scan")
        class MyScan(BaseModule):
            ...
    """
    def wrapper(cls: Type[BaseModule]) -> Type[BaseModule]:
        cls_name = name or cls.__name__.lower()
        if not cls.name:
            cls.name = cls_name
        if description and not cls.description:
            cls.description = description
        register_module(cls)
        return cls
    return wrapper


# ---------------------------------------------------------------------------
# Clean up exports
# ---------------------------------------------------------------------------

__all__ = [
    "BaseModule",
    "register_module",
    "unregister_module",
    "list_modules",
    "is_registered",
    "load_module",
    "get_module_class",
    "module",
]