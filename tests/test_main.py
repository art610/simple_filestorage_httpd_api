"""
Test module docstring title

Short description. Can help with autogenerate docs.
"""
from main import sample_sum_func


def test_sample_sum_func():
    """
    Simple test of sample_sum_func(a, b) from main.py
    """
    assert sample_sum_func(2, 2) == 4


# Input point if we directly run this script
if __name__ == "__main__":
    test_sample_sum_func()
