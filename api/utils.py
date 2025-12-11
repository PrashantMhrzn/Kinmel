import random

def generate_random_code():
    possible_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_code = ''
    # creating a random 6 character code
    for _ in range(6):
        short_code += random.choice(possible_characters)
    return short_code
