def create_admin_user(email: str, password: str) -> None:
    from turplanlegger.auth.utils import hash_password
    from turplanlegger.models.user import User

    admin = User(
        id='06335e84-2872-4914-8c5d-3ed07d2a2f16',
        name='Admin',
        last_name='Nimda',
        email=email,
        auth_method='basic',
        password=hash_password(password),
        private=True,
    )
    admin.create()
