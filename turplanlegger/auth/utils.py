import bcrypt


def hash_password(provided_pw: str) -> bytes:
    """Hashes a password using bcrypt.hashpw

    Args:
        provided_pw (str): Password to encrypt

    Returns:
        Encoded password (bytes)
    """
    return bcrypt.hashpw(provided_pw.encode('utf-8'), bcrypt.gensalt())


def check_password(hashed_pw: str, provided_pw: str) -> bool:
    """Checks for password match using bcrypt.checkpw

    Args:
        hashed_pw (str): hashed password (from db)
        provided_pw (str): password provided by user

    Returns:
        bool
    """
    return bcrypt.checkpw(provided_pw.encode('utf-8'), hashed_pw.encode('utf-8'))
