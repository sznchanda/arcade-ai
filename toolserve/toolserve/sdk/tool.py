from typing import Annotated, TypeVar, _AnnotatedAlias, Type, Callable, Any
import functools

T = TypeVar('T')
class SecretKey:
    def __init__(self, key: str):
        self.key = key

class Description:
    def __init__(self, description: str):
        self.description = description

def Param(type_: Type[T], description: str) -> Annotated[T, Description]:
    return Annotated[type_, Description(description)]

def Secret(type_: Type[T], key: str) -> Annotated[T, SecretKey]:
    return Annotated[type_, SecretKey(key)]

def tool(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper
