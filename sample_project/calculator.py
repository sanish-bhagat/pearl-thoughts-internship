"""
Calculator module with basic arithmetic operations.
"""

from utils.validators import validate_number
from logger import setup_logger

logger = setup_logger(__name__)


class Calculator:
    """A simple calculator class for basic arithmetic operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
        logger.debug("Calculator initialized")
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        validate_number(a)
        validate_number(b)
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract second number from first.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        validate_number(a)
        validate_number(b)
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        validate_number(a)
        validate_number(b)
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide first number by second.
        
        Args:
            a: Numerator
            b: Denominator
            
        Returns:
            Quotient of a and b
            
        Raises:
            ValueError: If b is zero
        """
        validate_number(a)
        validate_number(b)
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self) -> list:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()
        logger.info("History cleared")


class ScientificCalculator(Calculator):
    """Extended calculator with scientific functions."""
    
    import math
    
    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        validate_number(base)
        validate_number(exponent)
        result = self.math.pow(base, exponent)
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, number: float) -> float:
        """Calculate square root."""
        validate_number(number)
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = self.math.sqrt(number)
        self.history.append(f"√{number} = {result}")
        return result
