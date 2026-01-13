def add(a, b):
    """
    Adds Two Numbers
    """
    return a + b

def add_3(a, b, c):
    """
    Add 3 nnumbers, calls add() to get the sum of two no.
    and then simply add third no. to the result
    too get the final result
    """
    return add(a, b) + c

def mul(a, b):
    return a * b