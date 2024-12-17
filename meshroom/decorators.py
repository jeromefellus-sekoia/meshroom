from dataclasses import dataclass
import inspect
from pathlib import Path
from typing import Callable, Literal
from meshroom.model import Integration, Role, Mode, get_product, get_project_dir, get_integration

SetupFunctionType = Literal["setup", "teardown"]
_setup_functions: list["SetupFunction"] = []


@dataclass
class SetupFunction:
    product: str
    target_product: str | None
    role: Role
    topic: str
    func: Callable
    mode: Mode = "push"
    format: str | None = None
    keep_when_overloaded: bool = False
    order: Literal["first", "last"] | None = None
    title: str | None = None
    type: SetupFunctionType = "setup"

    def match(self, integration: Integration):
        return (
            self.product == integration.product
            and self.target_product in (None, integration.target_product)
            and self.role == integration.role
            and self.topic == integration.topic
            and self.mode == integration.mode
            and self.format in (None, integration.format)
        )

    def __lt__(self, other: "SetupFunction"):
        if other.order == "first":
            return False
        elif other.order == "last":
            return True
        return False

    def get_title(self):
        """Return this setup step's title, falling back to the setup function's name if not set"""
        return self.title or self.func.__name__

    @staticmethod
    def clear():
        _setup_functions.clear()

    @staticmethod
    def add(*args, **kwargs):
        _setup_functions.append(sf := SetupFunction(*args, **kwargs))
        return sf

    @staticmethod
    def get_all(type: SetupFunctionType | None = None):
        return [sf for sf in _setup_functions if type is None or sf.type == type]


# Product-level setup decorators


def setup_consumer(
    topic: str,
    title: str | None = None,
    mode: Mode = "push",
    keep_when_overloaded: bool = False,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a generic consumer setup step for the product where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        if func_file.parent.parent != get_project_dir() / "products":
            raise ValueError("consumer() decorator is allowed only in a product's setup.py")
        product = get_product(func_file.parent.name)
        SetupFunction.add(product.name, None, "consumer", topic, mode, func, keep_when_overloaded, order, title, "setup")
        return func

    return decorator


def teardown_consumer(
    topic: str,
    title: str | None = None,
    mode: Mode = "push",
    keep_when_overloaded: bool = False,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a generic consumer setup step for the product where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        if func_file.parent.parent != get_project_dir() / "products":
            raise ValueError("consumer() decorator is allowed only in a product's setup.py")
        product = get_product(func_file.parent.name)
        SetupFunction.add(product.name, None, "consumer", topic, mode, func, keep_when_overloaded, order, title, "teardown")
        return func

    return decorator


def setup_producer(
    topic: str,
    title: str | None = None,
    mode: Mode = "push",
    keep_when_overloaded: bool = False,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a generic producer setup step for the product where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        product = get_product(func_file.parent.name)
        if func_file.parent.parent != get_project_dir() / "products" or not product:
            raise ValueError("producer() decorator is allowed only in a product's setup.py")

        SetupFunction.add(product.name, None, "producer", topic, mode, func, keep_when_overloaded, order, title, "setup")
        return func

    return decorator


def teardown_producer(
    topic: str,
    title: str | None = None,
    mode: Mode = "push",
    keep_when_overloaded: bool = False,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a generic producer setup step for the product where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        product = get_product(func_file.parent.name)
        if func_file.parent.parent != get_project_dir() / "products" or not product:
            raise ValueError("producer() decorator is allowed only in a product's setup.py")

        SetupFunction.add(product.name, None, "producer", topic, mode, func, keep_when_overloaded, order, title, "teardown")
        return func

    return decorator


# Integration-level setup decorators


def setup(
    title: str | None = None,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a setup step for the integration where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        i = get_integration(func_file.with_suffix(""))
        if not i:
            raise ValueError("setup() decorator is allowed only in a product's setup.py")

        SetupFunction.add(i.product, i.target_product, i.role, i.topic, i.mode, func, True, order, title, "setup")
        return func

    return decorator


def teardown(
    title: str | None = None,
    order: Literal["first", "last"] | None = None,
):
    """Decorator to declare a function as a setup step for the integration where it resides"""

    def decorator(func: Callable):
        func_file = Path(inspect.getfile(func))
        i = get_integration(func_file.with_suffix(""))
        if not i:
            raise ValueError("setup() decorator is allowed only in a product's setup.py")

        SetupFunction.add(i.product, i.target_product, i.role, i.topic, i.mode, func, True, order, title, "teardown")
        return func

    return decorator
