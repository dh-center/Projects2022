import jwt


def get_jwt(name):
    # TODO: take secret from envs variables
    return jwt.encode(payload={"name": name}, key='my_super_secret_oneMedia').decode("utf-8")


JWT_HEADER_NAME = "X-One-Media"
