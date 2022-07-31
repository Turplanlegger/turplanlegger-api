import bcrypt


def hash_password(provided_pw) -> str:
    return bcrypt.hashpw(provided_pw.encode('utf-8'), bcrypt.gensalt())


def check_password(hashed_pw: str, provided_pw) -> bool:
    return bcrypt.checkpw(provided_pw.encode('utf-8'), hashed_pw.encode('utf-8'))


def create_token(user_id: int) -> str:
    from jwt import encode
    return encode({'test': 'token'}, 'test', algorithm='HS256')