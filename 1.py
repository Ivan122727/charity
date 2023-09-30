import hashlib

def get_sha256_hash(input_string):
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    return sha256_hash

inputstring = input()  # Замени "твоястрока" на свою строку в кодировке ASCII

sha256_hash = get_sha256_hash(input_string)

print(sha256_hash)