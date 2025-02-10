with open("./api/utils/rsa/private_key.pem", "rb") as key_file:
    PRIVATE_KEY = key_file.read()
with open("./api/utils/rsa/public_key.pem", "rb") as key_file:
    PUBLIC_KEY = key_file.read()
