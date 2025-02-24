from enum import Enum


class ParameterValueType(Enum):
    RAW = 0
    NORMALIZED = 1


def create_index_parameter(idx: int) -> str:
    return f"MTX:Index_{idx}"
