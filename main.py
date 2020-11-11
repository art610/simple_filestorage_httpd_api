"""
Some title of module docstring

Short description. Can help with autogenerate docs.
"""
# This is a sample Python script with typing

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes,
# files, tool windows, actions, and settings.


def sample_sum_func(first_number, second_number) -> int:
    """
    Sample function: get two arguments
    and return their sum
    """
    print('Find sum of %s and %s' % (first_number, second_number))
    return first_number + second_number


# Input point if we directly run this script
if __name__ == '__main__':
    print(type(sample_sum_func(2, 2)))
