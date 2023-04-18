from typing import Dict, List
from .internal_types import SupportsWrite
from .reader import PythonValue
from json import dumps as jd
import random

_kws: Dict[str, List[str]] = {
    "have": ["have", "has", "'ve"],
    "that": ["that", "this", "these", "those"],
    "true": ["true", "falsen't"],
    "false": ["false", "truen't"],
    "is": [" is", " are", "'s", "'re", " do", " does", " be"],
    "haven't": ["haven't", "hasn't", "'ve'n't"],
}


def _random_kw(kw_key: str) -> str:
    return random.choice(_kws[kw_key])


def _add_tab(text: str) -> str:
    tab_char = "  "
    if not text:
        return text
    return tab_char + text.replace("\n", "\n" + tab_char)


def _make_list(obj: List[PythonValue]) -> str:
    entries = "\n".join(map(dumps, obj))
    return f"{_random_kw('have')}\n{_add_tab(entries)}\n{_random_kw('that')}{_random_kw('is')} all"


def _make_dict(obj: Dict[str, PythonValue], is_toplevel: bool = False) -> str:
    sep = "\n\n" if is_toplevel else "\n"

    entries = sep.join(
        f"{_dumps_inner(key)}{_random_kw('is')} {_dumps_inner(value)}"
        for key, value in obj.items()
    )

    if is_toplevel:
        return entries

    return f"{_random_kw('have')}\n{_add_tab(entries)}\n{_random_kw('that')}{_random_kw('is')} all"


def dump(file: SupportsWrite[str], obj: PythonValue) -> None:
    file.write(dumps(obj))


def dumps(obj: PythonValue) -> str:
    return _dumps_inner(obj, True)


def _dumps_inner(obj: PythonValue, is_toplevel: bool = False) -> str:
    if isinstance(obj, list):
        return _make_list(obj)
    if isinstance(obj, dict):
        return _make_dict(obj, is_toplevel)
    if isinstance(obj, bool):
        return _random_kw(["false", "true"][obj])
    if obj is None:
        return _random_kw("haven't")

    return jd(obj)
