import pytest
from lib.Utils.loggingSystem import LoggingSystem

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5


if __name__ == '__main__':
    test_answer()