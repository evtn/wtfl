from __future__ import annotations
from typing import Protocol, TypeVar, Union, List
from typing_extensions import Literal
import random

KeyChain = List[str]


def _randomchar(_: int) -> str:
    return random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()[]{},./\\")


ARRAY_KEY = "$arr" + "".join(map(_randomchar, range(10)))


class Operation:
    op_type: str = "noop"
    offset: int = 0


class Also(Operation):
    pass


class Constraint(Operation):
    op_type = "constraint"

    def __init__(self, ctype: ConstraintType, key: KeyChain, value: Value = None):
        self.ctype = ctype
        self.key = tuple(key)
        self.value = value

    def key_repr(self):
        return " of ".join(map(repr, reversed(self.key)))

    def __repr__(self):
        return f"{self.key} {self.ctype}, {self.value}"

    def check(self, value):
        if self.ctype == "hastobe":
            if value != self.value:
                raise ValueError(
                    f"{self.key_repr()} has to be {self.value}, not {value}"
                ) from None
            return

        if self.ctype == "cantbe":
            if value == self.value:
                raise ValueError(f"{self.key_repr()} cannot be {self.value}")

        if self.ctype == "cant_exist":
            raise ValueError(f"{self.key_repr()} cannot exist")


class Assign(Operation):
    op_type = "assign"

    def __init__(self, key: KeyChain, value: Value):
        self.key = key
        self.value = value

    def rebase(self, path: KeyChain) -> Assign:
        op = Assign(path + self.key, self.value)
        op.offset = self.offset
        return op

    def unwind(self, prefix: KeyChain) -> List[Assign]:
        if not isinstance(self.value, Object):
            return [self.rebase(prefix)]

        return self.value.flatten_paths(prefix + self.key)

    def __repr__(self):
        return f"{self.key} = {self.value}"


class Object:
    def __init__(self, pairs: List[Assign]):
        self.pairs = pairs

    def __repr__(self):
        return f'[{",".join(map(repr, self.pairs))}]'

    def flatten_paths(self, prefix: KeyChain) -> List[Assign]:
        if not self.pairs:
            return [Assign(prefix, self)]
        new_pairs = []
        for pair in self.pairs:
            new_pairs.extend(pair.unwind(prefix))
        return new_pairs


_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsRead(Protocol[_T_co]):
    def read(self, __length: int = ...) -> _T_co:
        ...


# stable
class SupportsWrite(Protocol[_T_contra]):
    def write(self, __s: _T_contra) -> object:
        ...


Value = Union[str, float, bool, None, Object]


ConstraintType = Union[Literal["hastobe"], Literal["cantbe"], Literal["cant_exist"]]
