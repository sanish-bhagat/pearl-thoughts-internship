"""
Unit tests for the calculator module.
"""

import unittest
from calculator import Calculator, ScientificCalculator


class TestCalculator(unittest.TestCase):
    """Test cases for Calculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition operation."""
        result = self.calc.add(5, 3)
        self.assertEqual(result, 8)
    
    def test_subtract(self):
        """Test subtraction operation."""
        result = self.calc.subtract(10, 4)
        self.assertEqual(result, 6)
    
    def test_multiply(self):
        """Test multiplication operation."""
        result = self.calc.multiply(3, 4)
        self.assertEqual(result, 12)
    
    def test_divide(self):
        """Test division operation."""
        result = self.calc.divide(10, 2)
        self.assertEqual(result, 5)
    
    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)
    
    def test_history(self):
        """Test calculation history."""
        self.calc.add(1, 2)
        self.calc.subtract(5, 3)
        history = self.calc.get_history()
        self.assertEqual(len(history), 2)


class TestScientificCalculator(unittest.TestCase):
    """Test cases for ScientificCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calc = ScientificCalculator()
    
    def test_power(self):
        """Test power operation."""
        result = self.calc.power(2, 3)
        self.assertEqual(result, 8)
    
    def test_sqrt(self):
        """Test square root operation."""
        result = self.calc.sqrt(16)
        self.assertEqual(result, 4)
