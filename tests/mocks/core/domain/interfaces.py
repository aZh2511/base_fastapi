from core.domain.interfaces import IPasswordHasher


class FakePasswordHasher(IPasswordHasher):
    @staticmethod
    def hash_password(password: str) -> str:
        return f"hashed:{password}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"
