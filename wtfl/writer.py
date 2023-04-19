from __future__ import annotations
from typing import Callable, Dict, List, Tuple
from .internal_types import SupportsWrite
from .reader import PythonValue
from json import dumps as jd
import random
import math

_kws: Dict[str, List[str]] = {
    "have": ["have", "has", "'ve"],
    "that": ["that", "this", "these", "those"],
    "true": ["true", "falsen't"],
    "false": ["false", "truen't"],
    "is": [" is", " are", "'s", "'re", " do", " does", " be"],
    "haven't": ["haven't", "hasn't", "'ve'n't"],
}


class WTFLEncoder:
    def __init__(
        self,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        indent: int | str | None = 2,
        default: Callable[[object], str] | None = None,
        sort_keys: bool = False,
    ):
        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.default = default
        self.sort_keys = sort_keys
        self.indent = "  "
        self.statement_sep = "\n" if indent is not None else " "
        self.also = " also" if "\n" not in self.statement_sep else ""

        if isinstance(indent, int):
            if indent >= 0:
                self.indent = " " * indent
        elif isinstance(indent, str):
            self.indent = indent

    def random_kw(self, kw_key: str) -> str:
        return random.choice(_kws[kw_key])

    def add_tab(self, text: str) -> str:
        if not (self.indent or text):
            return text
        return self.indent + text.replace("\n", "\n" + self.indent)

    def make_list(self, obj: List[PythonValue]) -> str:
        if not obj:
            return f"{self.random_kw('have')} 0"

        tail = f"{self.random_kw('that')}{self.also}"

        entries = filter(None, map(self.dumps, obj))

        result = [
            self.random_kw("have"),
            self.add_tab(self.statement_sep.join(entries)),
            tail,
        ]
        return self.statement_sep.join(result)

    def make_dict(self, obj: Dict[str, PythonValue], is_toplevel: bool = False) -> str:
        sep = self.statement_sep * (1 + is_toplevel)

        obj_iter = obj.items() if not self.sort_keys else sorted(obj.items())

        def pair_filter(kv: Tuple[str, str]) -> bool:
            return all(kv)

        filtered = filter(
            pair_filter,
            [(self.dumps(key), self.dumps(value)) for key, value in obj_iter],
        )

        entries = (f"{k}{self.random_kw('is')} {v}" for (k, v) in filtered)

        if is_toplevel:
            return sep.join(entries)

        tail = f"{self.random_kw('that')}{self.also}"

        result = [self.random_kw("have"), self.add_tab(sep.join(entries)), tail]

        return sep.join(result)

    def dumps(self, obj: PythonValue, is_toplevel: bool = False) -> str:
        if isinstance(obj, list):
            return self.make_list(obj)

        if isinstance(obj, dict):
            return self.make_dict(obj, is_toplevel)

        if isinstance(obj, bool):
            return self.random_kw(["false", "true"][obj])

        if obj is None:
            return self.random_kw("haven't")

        if (
            isinstance(obj, (float, int))
            and obj not in restricted_floats
            and not math.isnan(obj)
        ):
            return jd(obj)

        if isinstance(obj, str):
            return jd(obj, ensure_ascii=self.ensure_ascii)

        if self.skipkeys:
            return ""

        if self.default:
            return self.dumps(self.default(obj))

        raise TypeError(
            "Invalid data type for serialization. Provide skipkeys=True or default handler"
        )


restricted_floats = {
    float("inf"),
    -float("inf"),
}


def dump(
    file: SupportsWrite[str],
    obj: PythonValue,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    indent: int | str | None = 2,
    default: Callable[[object], str] | None = None,
    sort_keys: bool = False,
) -> None:
    file.write(
        dumps(
            obj,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            indent=indent,
            default=default,
            sort_keys=sort_keys,
        )
    )


def dumps(
    obj: PythonValue,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    indent: int | str | None = 2,
    default: Callable[[object], str] | None = None,
    sort_keys: bool = False,
) -> str:
    return WTFLEncoder(
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        indent=indent,
        default=default,
        sort_keys=sort_keys,
    ).dumps(obj, True)
