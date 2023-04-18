# type: ignore

from lark_dynamic import (
    Alias,
    Grammar,
    Group,
    Literal,
    Many,
    ManySeparated,
    Maybe,
    Modifier,
    RegExp,
    Some,
    SomeSeparated,
)

g = Grammar()

g.WS = Many(Literal(" ") | r"\n")
g.COMMENT = RegExp(r"\.\.\..*\n?")
g.make_directive("ignore", g.WS)
g.make_directive("ignore", g.COMMENT)

g.AND[3] = "and"
g.BUT[2] = "but"
g.IS[2] = Literal("is") | "are" | "'s" | "'re" | "do" | "does" | "be"
g.ISNT[2] = Literal("isn't") | "aren't" | "'sn't" | "'ren't"

g.OF[2] = "of"
g.THAT[2] = Literal("that") | "this" | "these" | "those"
g.THERE[2] = "there"
g.HAVE[2] = Literal("have") | "has" | "'ve"
g.HAVENT[2] = Literal("haven't") | "hasn't" | "'ven't"

g.CAN[2] = "can"
g.CANT[2] = Literal("cannot") | "can't"
g.BOOL[2] = RegExp(r"(true|false)(n't)?")
g.RETURN[2] = "return"
g.SKIP[2] = "skip"
g.STAY[2] = "stay"
g.TO[2] = "to"


g.PREFIX[2] = RegExp(r"\b(an?|the|d[eu]|l[ea]|des|les|um)\b")

g._keyword_name = (
    g.IS
    | g.AND
    | g.ISNT
    | g.OF
    | g.THAT
    | g.THERE
    | g.HAVE
    | g.CAN
    | g.CANT
    | g.RETURN
    | g.SKIP
    | g.STAY
    | g.TO
)

g.file = Some(g.statement | g._inline_statements)

g.also = Maybe(g.AND | g.BUT), "also"
g._inline_statements = ManySeparated(g.also, g.statement)

g.statement = g.assign_key | g.time_travel | g.constraint

g.assign_key = g.key, g.IS, g.value

g.key = SomeSeparated(g.OF, g.base_key)

g.constraint = Modifier.INLINE_SINGLE(
    g.can_exist | g.cant_exist | g.can_be | g.cant_be | g.has_to_be
)

g.can_exist = g.key, g.CAN, g.IS
g.cant_exist = g.key, g.CANT, g.IS
g.can_be = g.key, g.CAN, g.IS, g.value
g.cant_be = g.key, g.CANT, g.IS, g.value
g.has_to_be = g.key, g.HAVE, g.TO, g.IS, g.value

g.base_key = Maybe(g.key_prefix), Group(g._name | g._atom)
g.key_prefix = g.PREFIX | g.BUT

g.NAME_START = RegExp("[A-Za-z_-]")
g.NAME_CHARS = RegExp("[A-Za-z0-9_-]")

g.NAME = g.NAME_START, Some(g.NAME_CHARS)

g._name = g.NAME | g._keyword_name

g.value = g._atom | g.empty_array | g.object | g.array
g._atom = g.number | g.bool | g.string | g.none

g.none = g.HAVENT
g.bool = g.BOOL

g.object = g.HAVE, Some(g.assign_key), g.OBJECT_TAIL
g.array = g.HAVE, Many(g.value), g.OBJECT_TAIL
g.empty_array = g.HAVE, "0"

g.OBJECT_TAIL[3] = Group(g.THERE | g.THAT), g.TAIL_OTHER
g.TAIL_OTHER = RegExp(r".+?(?=also|\n|$)")

g.number = g.negative

g.MINUS = "-"

g.negative = Modifier.INLINE_SINGLE(Maybe(g.MINUS), Group(g.integer | g.float))

g.integer[2] = (
    Alias.hexadecimal(g.HEX_INT)
    | Alias.octal(g.OCT_INT)
    | Alias.binary(g.BIN_INT)
    | Alias.roman(g.ROMAN_INT)
    | Alias.decimal(g.DEC_WTF)
    | Alias.duodecimal(g.DUODEC_INT)
    | Alias.vigesimal(g.VIG_INT)
    | Alias.unary_int(g.UNARY)
    | g.INT
)

g.INT[1] = g.DEC_INT_BASE

g._DIGIT_DIV = "_"
g.BIN_DIGIT = Literal("0") | "1"
g.OCT_DIGIT = g.BIN_DIGIT | "2" | "3" | "4" | "5" | "6" | "7"
g.DEC_DIGIT = g.OCT_DIGIT | "8" | "9"
g.DUODEC_DIGIT = g.DEC_DIGIT | "A" | "a" | "B" | "b"
g.HEX_DIGIT = g.DUODEC_DIGIT | "C" | "c" | "D" | "d" | "E" | "e" | "F" | "f"
g.VIG_DIGIT = g.HEX_DIGIT | "G" | "g" | "H" | "h" | "I" | "i" | "J" | "j"

g.BIN_INT[2] = (
    Literal("0b", "i"),
    Many(g.BIN_DIGIT),
    Some(g._DIGIT_DIV, Many(g.BIN_DIGIT)),
)
g.OCT_INT[2] = (
    Literal("0o", "i"),
    Many(g.OCT_DIGIT),
    Some(g._DIGIT_DIV, Many(g.OCT_DIGIT)),
)
g.DEC_INT_BASE = Many(g.DEC_DIGIT), Some(g._DIGIT_DIV, Many(g.DEC_DIGIT))
g.DUODEC_INT[2] = (
    Literal("0z", "i"),
    Many(g.DUODEC_DIGIT),
    Some(g._DIGIT_DIV, Many(g.DUODEC_DIGIT)),
)
g.HEX_INT[2] = (
    Literal("0x", "i"),
    Many(g.HEX_DIGIT),
    Some(g._DIGIT_DIV, Many(g.HEX_DIGIT)),
)
g.VIG_INT[2] = (
    Literal("0v", "i"),
    Many(g.VIG_DIGIT),
    Some(g._DIGIT_DIV, Many(g.VIG_DIGIT)),
)

g.UNARY[2] = Literal("0u", "i"), Many("1")
g.DEC_WTF[2] = Literal("0d", "i"), g.DEC_INT_BASE

g.ROMAN_DIGIT = (
    Literal("I", "i")
    | Literal("V", "i")
    | Literal("X", "i")
    | Literal("L", "i")
    | Literal("C", "i")
    | Literal("D", "i")
    | Literal("M", "i")
)
g.ROMAN_INT[2] = Literal("0r", "i"), Many(g.ROMAN_DIGIT)

g.FLOAT_DEC_BASE = (
    Group(g.DEC_INT_BASE, ".", Maybe(g.DEC_INT_BASE))
    | (".", g.DEC_DIGIT)
    | g.DEC_INT_BASE
)
g.FLOAT = g.FLOAT_DEC_BASE, Maybe(
    Literal("e", "i"), Maybe(Literal("-") | "+"), g.DEC_INT_BASE
)
g.float = g.FLOAT
g.STRING = RegExp(r'"([^"\\]|\\.)*"')
g.string = g.STRING

g.time_travel = (
    Group(g.past_travel | g.present_travel | g.future_travel),
    g.AND,
    g.statement,
)
g.past_travel = g.RETURN, g.integer
g.present_travel = g.STAY
g.future_travel = g.SKIP, g.integer
