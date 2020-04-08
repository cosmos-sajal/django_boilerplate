import random


def get_random_number(length=6):
    """
    Generate a random number of fixed length
    """
    numbers = "1234567890"

    return ''.join(random.choice(numbers) for i in range(length))


def get_random_string(length=10):
    """
    Generates a random string of fixed length
    """
    string = "abcdefghijklmnopqrstuvwxyz"

    return ''.join(random.choice(string) for i in range(length))
