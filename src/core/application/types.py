from typing import Annotated, TypeVar

from pydantic import WrapValidator

T = TypeVar("T")
FromValueObjectType = Annotated[T, WrapValidator(lambda v, handler: handler(v.value))]
