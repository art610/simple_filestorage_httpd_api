"""
Данный модуль будет основной точкой входа
"""
import server


HOST = 'localhost'
PORT = 9000


def sample_sum_func(first_number, second_number) -> int:
    """
    Sample function: get two arguments
    and return their sum
    """
    print('Find sum of %s and %s' % (first_number, second_number))
    return first_number + second_number


# Input point if we directly run this script
if __name__ == '__main__':
    server.run_server()
