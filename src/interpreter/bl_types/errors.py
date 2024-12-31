"""Basic errors"""


from .base import BLError

# pylint: disable=unused-import
from .base import error_not_implemented  # noqa: F401


error_div_by_zero = BLError("Division by zero")
error_out_of_range = BLError("Index out of range: {}")
error_key_nonexistent = BLError("Non-existent key: {}")
error_var_nonexistent = BLError("Variable {} is undefined")
error_wrong_argc = BLError("Function {} needs exactly {} arguments")
error_module_var_nonexistent = BLError("Module {} doesn't have variable {}")
error_include_syntax = BLError("Error in include's syntax:\n{}")
error_inside_include = BLError(
    "Error inside include at line {}, column {}: {}"
)
error_invalid_include = BLError("Invalid include '{}'")
error_incorrect_rettype_to_bool = BLError("__bool__() must return a Bool")
error_class_attr_nonexistent = BLError("Class {} has no attribute {}")
error_incorrect_rettype_to_string = BLError(
    "__dump__() and to_string() must return a String"
)
