# This is a sample Python script with typing

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def sample_sum_func(a, b) -> int:
    print('Find sum of %s and %s' % (a, b))
    return a + b


# Input point if we directly run this script
if __name__ == '__main__':
    print(type(sample_sum_func(2, 2)))
