import pytest
from calculator import add, multiply

# Test cases for add function
def test_add_positive_numbers():
   assert add(2, 3) == 5

def test_add_negative_numbers():
   assert add(-1, -1) == -2

def test_add_zero():
   assert add(0, 5) == 5
   assert add(5, 0) == 5

def test_add_mixed_signs():
   assert add(-1, 3) == 2
   assert add(3, -1) == 2

# Test cases for multiply function
def test_multiply_positive_numbers():
   assert multiply(2, 3) == 6

def test_multiply_with_zero():
   assert multiply(0, 5) == 0
   assert multiply(5, 0) == 0

def test_multiply_negative_numbers():
   assert multiply(-2, -3) == 6

def test_multiply_mixed_signs():
   assert multiply(-2, 3) == -6
   assert multiply(2, -3) == -6
