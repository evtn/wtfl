from __future__ import annotations
import typing
import codecs
from typing import Callable, List, Dict, Tuple

from lark import Lark, Transformer
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from .internal_types import ARRAY_KEY, Also, Constraint, Object, Assign, Operation
from .grammar import g as grammar  # type: ignore


def parse(s: str, parse_funcs: ParseFuncs) -> List[Operation]:
    (
        parse_float_custom,
        parse_int_custom,
        parse_roman_custom,
        parse_numbers_custom,
    ) = parse_funcs

    if parse_float_custom:
        WTFLTransformer.parse_float = parse_float_custom

    if parse_int_custom:
        WTFLTransformer.parse_int = parse_int_custom

    if parse_roman_custom:
        WTFLTransformer.parse_roman = parse_roman_custom

    if parse_numbers_custom:
        WTFLTransformer.parse_numbers = parse_numbers_custom

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

    finally:
        WTFLTransformer.parse_float = parse_float
        WTFLTransformer.parse_int = parse_int
        WTFLTransformer.parse_roman = parse_roman
        WTFLTransformer.parse_numbers = parse_numbers


def _unpack(_: object, tokens: List[object]) -> object:
    return tokens[0]


def make_roman_digit(i: int) -> int:
    base: int = (i % 2) * 4 + 1
    exponent: int = 10 ** (i // 2)

    return base * exponent


roman_digits: Dict[str, int] = {k: make_roman_digit(i) for i, k in enumerate("IVXLCDM")}


def parse_float(s: str) -> PythonValue:
    return float(s)


def parse_int(s: str) -> PythonValue:
    return int(s)


def parse_roman(s: str) -> PythonValue:
    num = s[2:].upper()
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


def parse_numbers(s: str) -> PythonValue:
    if s[1] == "u":
        return len(s) - 2

    bases = {
        "b": 2,
        "o": 8,
        "d": 10,
        "z": 12,
        "v": 20,
    }
    return int(s[2:], bases[s[1]])


class WTFLTransformer(Transformer):
    value = _unpack
    number = _unpack
    parse_float: ParseFunc = parse_float
    parse_int: ParseFunc = parse_int
    parse_roman: ParseFunc = parse_roman
    parse_numbers: ParseFunc = parse_numbers

    def float(self, tokens):
        s = tokens[0]

        if "." in s:
            return WTFLTransformer.parse_float(s)
        return WTFLTransformer.parse_int(s)

    def integer(self, tokens):
        return WTFLTransformer.parse_int(tokens[0])

    def negative(self, tokens):
        return -tokens[1]

    def roman(self, tokens):
        return WTFLTransformer.parse_roman(tokens[0])

    def hexadecimal(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

    def octal(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

    def binary(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

    def duodecimal(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

    def vigesimal(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

    def unary_int(self, tokens):
        return WTFLTransformer.parse_numbers(tokens[0])

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


class TransformConfig:
    parse_float = float
    parse_int = int
    parse_roman = WTFLTransformer.parse_roman


transformer = WTFLTransformer()


_parser = Lark(
    grammar=grammar.generate(),  # type: ignore
    parser="lalr",
    start="file",
    transformer=transformer,
)

from .reader import PythonValue

ParseFunc = Callable[[str], PythonValue]
ParseFuncs = Tuple[
    ParseFunc | None, ParseFunc | None, ParseFunc | None, ParseFunc | None
]
