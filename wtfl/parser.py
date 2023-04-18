from __future__ import annotations
import typing
import codecs
from typing import List, Dict

from lark import Lark, Transformer
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from .internal_types import ARRAY_KEY, Also, Constraint, Object, Assign, Operation
from .grammar import g as grammar  # type: ignore


def parse(s: str) -> List[Operation]:
    try:
        return typing.cast(List[Operation], _parser.parse(s))

    except UnexpectedCharacters as e:  # type: ignore[misc]
        raise ValueError(
            f"Unexpected characters at line {e.line} column {e.column}: {e.char}\n{e.get_context(s)}"  # type: ignore[misc]
        ) from None

    except UnexpectedToken as e:  # type: ignore[misc]
        raise ValueError(
            f"Unexpected token at line {e.line} column {e.column}: {e.token}\n{e.get_context(s, 100)}"  # type: ignore[misc]
        ) from None


def _unpack(_: object, tokens: List[object]) -> object:
    return tokens[0]


def make_roman_digit(i: int) -> int:
    base: int = (i % 2) * 4 + 1
    exponent: int = 10 ** (i // 2)

    return base * exponent


roman_digits: Dict[str, int] = {k: make_roman_digit(i) for i, k in enumerate("IVXLCDM")}


class WTFLTransformer(Transformer):
    value = _unpack
    number = _unpack

    def float(self, tokens):
        value = float(tokens[0])
        if value.is_integer():
            return int(value)
        return value

    def integer(self, tokens):
        return int(tokens[0])

    def negative(self, tokens):
        return -tokens[1]

    def roman(self, tokens):
        num = tokens[0][2:].upper()
        result = 0
        current = [0, 0]
        for digit in num:
            digit_value = roman_digits[digit]
            if current[0] == digit_value:
                current[1] += 1
            else:
                part_value = current[0] * current[1]
                if digit_value > part_value:
                    result -= part_value
                else:
                    result += part_value
                current = [digit_value, 1]
        return result + current[0] * current[1]

    def hexadecimal(self, tokens):
        return int(tokens[0], 16)

    def octal(self, tokens):
        return int(tokens[0], 8)

    def binary(self, tokens):
        return int(tokens[0], 2)

    def duodecimal(self, tokens):
        return int(tokens[0][2:], 12)

    def vigesimal(self, tokens):
        return int(tokens[0][2:], 20)

    def string(self, tokens):
        decoder = codecs.getdecoder("unicode_escape")
        return decoder(tokens[0][1:-1])[0]

    def object(self, tokens):
        [_, *pairs, _] = tokens
        return Object(pairs)

    def array(self, tokens):
        [_, *values, _] = tokens

        pairs = [Assign([str(i)], value) for i, value in enumerate(values)]
        pairs.insert(0, Assign([ARRAY_KEY], True))

        return Object(pairs)

    def empty_array(self, _):
        return self.array([None, None])

    def base_key(self, tokens):
        return str(tokens[-1])

    def key(self, tokens):
        return tokens[::-2]

    def assign_key(self, tokens):
        [keys, _, value] = tokens
        return Assign(keys, value)

    def statement(self, tokens):
        return tokens[0]

    def also(self, _):
        return Also()

    def can_exist(self, _):
        return Operation()

    def cant_exist(self, tokens):
        return Constraint(
            "cant_exist",
            tokens[0],
        )

    def can_be(self, _):
        return Operation()

    def cant_be(self, tokens):
        return Constraint("cantbe", tokens[0], tokens[-1])

    def has_to_be(self, tokens):
        [key, *_, value] = tokens
        return Constraint("hastobe", key, value)

    def file(self, statements):
        return [s for s in statements if not isinstance(s, Also)]

    def past_travel(self, tokens):
        return -tokens[-1]

    def present_travel(self, _):
        return 0

    def future_travel(self, tokens):
        return tokens[-1]

    def time_travel(self, tokens):
        [offset, _, operation] = tokens
        operation.offset += offset
        return operation

    def none(self, _):
        return None

    def bool(self, tokens):
        is_true = "true" in tokens[0]
        is_not = "n't" in tokens[0]

        return is_true != is_not

    def key_prefix(self, _):
        return None


_parser = Lark(
    grammar=grammar.generate(),  # type: ignore
    parser="lalr",
    start="file",
    transformer=WTFLTransformer(),
)
