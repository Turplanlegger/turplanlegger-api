from turplanlegger.app import db

JSON = Dict[str, any]


class User:
    
    def __init__(self, name: str, last_name: str, email: str)