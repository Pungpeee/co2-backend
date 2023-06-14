import math
import random
import string


def generate_token(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(length))

def generate_OTP():
    return ''.join(random.choice(string.digits) for _ in range(6))