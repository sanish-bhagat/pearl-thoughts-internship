"""
Helper functions for formatting and input validation.
"""

from typing import Union
from .validators import validate_number


def format_result(value: Union[int, float], precision: int = 2) -> str:
    """
    Format a numeric result for display.
    
    Args:
        value: Numeric value to format
        precision: Number of decimal places (default: 2)
        
    Returns:
        Formatted string representation
    """
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return f"{value:.{precision}f}"
    else:
        return str(value)


def validate_input(user_input: str) -> float:
    """
    Validate and convert user input to float.
    
    Args:
        user_input: String input from user
        
    Returns:
        Converted float value
        
    Raises:
        ValueError: If input cannot be converted to float
    """
    try:
        return float(user_input.strip())
    except ValueError:
        raise ValueError(f"Invalid number: {user_input}")


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"
