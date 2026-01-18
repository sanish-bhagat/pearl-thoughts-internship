"""
Main entry point for the sample calculator application.
"""

from calculator import Calculator
from utils.helpers import format_result, validate_input
from logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main function to run the calculator."""
    logger.info("Starting calculator application")
    
    calc = Calculator()
    
    # Get user input
    try:
        num1 = validate_input(input("Enter first number: "))
        num2 = validate_input(input("Enter second number: "))
        operation = input("Enter operation (+, -, *, /): ")
        
        # Perform calculation
        if operation == "+":
            result = calc.add(num1, num2)
        elif operation == "-":
            result = calc.subtract(num1, num2)
        elif operation == "*":
            result = calc.multiply(num1, num2)
        elif operation == "/":
            result = calc.divide(num1, num2)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Format and display result
        formatted = format_result(result)
        print(f"Result: {formatted}")
        logger.info(f"Calculation completed: {num1} {operation} {num2} = {result}")
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
