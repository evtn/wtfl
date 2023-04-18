from __future__ import annotations
from json import dumps
from logging import warn
from typing import Sequence, Union
from .internal_types import (
    ARRAY_KEY,
    Constraint,
    KeyChain,
    Object,
    Operation,
    SupportsRead,
    Value,
)
from .parser import parse, Assign

StateValue = Union[str, float, bool, None, "Store"]
PythonValue = Union[
    str, float, bool, None, dict[str, "PythonValue"], list["PythonValue"]
]


class Store:
    def __init__(self):
        self.keys: dict[str, StateValue] = {}
        self.is_array = False
        self.can_be_array = True

    def add_key(self, key: str, value: StateValue):
        if key == ARRAY_KEY and self.can_be_array:
            self.is_array = True
            return

        if self.can_be_array:
            if key.lstrip("-").isnumeric():
                try:
                    int(key)
                    self.keys[key] = value
                    return
                except:
                    pass
            self.can_be_array = False

        self.is_array = False
        self.keys[key] = value

    def to_python_value(self) -> PythonValue:
        if self.is_array:
            result_list: list[PythonValue] = []
            last_index = -1
            warned_about_holes = False

            for key, value in sorted(self.keys.items()):
                index = int(key)
                if index < 0:
                    continue
                if (index - last_index - 1) and not warned_about_holes:
                    warn("Warning: array holes are removed. Check your array indices")
                    warned_about_holes = True

                if isinstance(value, Store):
                    result_list.append(value.to_python_value())
                else:
                    result_list.append(value)

                last_index = index
            return result_list

        result_dict: dict[str, PythonValue] = {}

        for key, value in self.keys.items():
            if isinstance(value, Store):
                py_value = value.to_python_value()
            else:
                py_value = value

            result_dict[str(key)] = py_value

        return result_dict

    def __contains__(self, key):
        return key in self.keys

    def __getitem__(self, key: str):
        return self.keys[key]

    def __setitem__(self, key: str, value: StateValue):
        self.add_key(key, value)


class ReadState:
    def __init__(self):
        self.constraints: dict[tuple[str, ...], list[Constraint]] = {}
        self.keys = Store()

    def create_path(self, path: KeyChain):
        store = self.keys

        for key in path:
            if key in store:
                new_store = store[key]
                if not isinstance(new_store, Store):
                    raise ValueError("what?", path, key, new_store)
            else:
                new_store = Store()
                store[key] = new_store

            store = new_store

        return store

    def assign_path(self, path: KeyChain, value: Value):
        store = self.create_path(path[:-1])

        last_key = path[-1]

        assert not isinstance(value, Object)

        store[last_key] = value

    def add_constraint(self, constraint: Constraint):
        key = constraint.key

        if key not in self.constraints:
            self.constraints[key] = []

        self.constraints[key].append(constraint)

    def check_constraint(self, op: Assign):
        path = tuple(op.key)
        constraints = self.constraints.get(path)

        if not constraints:
            return

        for constraint in constraints:
            constraint.check(op.value)

    def assign(self, op: Assign):
        self.check_constraint(op)
        self.assign_path(op.key, op.value)

    def to_dict(self):
        return self.keys.to_python_value()


class Reader:
    def read(self, s: str) -> ReadState:
        state = ReadState()
        tree = parse(s.lower())

        statements: list[tuple[Operation, int]] = []

        for i, operation in enumerate(tree):
            statements.extend((op, i) for op in self.process_operation(operation))

        def key_func(statement: tuple[Operation, int]) -> float:
            [operation, index] = statement

            if operation.offset:
                return index + operation.offset - 1 / 100000

            return index

        for statement in sorted(statements, key=key_func):
            self.apply_operation(statement[0], state)

        return state

    def process_operation(self, operation: Operation) -> Sequence[Operation]:
        if operation.op_type == "noop":
            return []
        if isinstance(operation, Assign):
            return operation.unwind([])
        return [operation]

    def apply_operation(self, operation: Operation, state: ReadState):
        if isinstance(operation, Assign):
            state.assign(operation)
        if isinstance(operation, Constraint):
            state.add_constraint(operation)


def loads(s: str):
    state = Reader().read(s)
    return state.to_dict()


def load(file: SupportsRead[str]):
    return loads(file.read())
