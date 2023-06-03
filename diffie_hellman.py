# use this library to get values for the diffie hellman key exchange
# with this library you can generate a 128 byte (16 digit long) key

import random

GENERATOR = 2
PRIME = 2543

def gen_secret():
    return random.randint(1, PRIME-1)


def get_public(secret):
    return (GENERATOR ** secret) % PRIME


def get_key(other_public, secret):
    # generates the key according to diffie hellman
    key = (other_public ** secret) % PRIME
    
    # padds it so it has 16 digits and therefore be  128 byte big
    key = (str(key).ljust(16, '0')).encode()

