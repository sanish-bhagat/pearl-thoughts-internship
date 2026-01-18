"""
Validation functions for numeric inputs.
"""

from typing import Union


def validate_number(value: Union[int, float]) -> None:
    """
    Validate that a value is a number.
    
    Args:
        value: Value to validate
        
    Raises:
        TypeError: If value is not a number
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected number, got {type(value).__name__}")


def validate_positive(value: Union[int, float]) -> None:
    """
    Validate that a number is positive.
    
    Args:
        value: Number to validate
        
    Raises:
        ValueError: If value is not positive
    """
    validate_number(value)
    if value <= 0:
        raise ValueError(f"Expected positive number, got {value}")


def validate_range(value: Union[int, float], min_val: float, max_val: float) -> None:
    """
    Validate that a number is within a range.
    
    Args:
        value: Number to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Raises:
        ValueError: If value is outside the range
    """
    validate_number(value)
    if not (min_val <= value <= max_val):
        raise ValueError(f"Value {value} is outside range [{min_val}, {max_val}]")
