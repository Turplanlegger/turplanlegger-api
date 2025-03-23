from uuid import uuid4


def create_admin_user(email: str, password: str) -> None:
    from turplanlegger.auth.utils import hash_password
    from turplanlegger.models.user import User

    admin = User(
        id=uuid4(),
        name='Admin',
        last_name='Nimda',
        email=email,
        auth_method='basic',
        password=hash_password(password),
        private=True,
    )
    admin.create()
