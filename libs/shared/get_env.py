import os
from typing import Optional, TypeVar

ValType = TypeVar('ValType')
def get_env(key: str, target_type: type, default: Optional[ValType] = None) -> ValType:
    value = os.getenv(key, default=default)
    if (value == None):
        raise KeyError(f"Environment variable {key} does not exist")
    if (not target_type):
        target_type = str
    return target_type(value)