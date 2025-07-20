from core.domain import value_objects as vo
import pytest
from core.domain.exceptions import PasswordIsNotSecure


@pytest.mark.parametrize(
    ["password", "is_valid"],
    [
        ("a", False),
        ("a1", False),
        ("a1!", False),
        ("a1!B", False),
        ("a" * 8, False),
        ("a" * 8 + "!", False),
        ("a" * 8 + "!" + "2", False),
        ("a" * 8 + "!" + "2" + "A", True),
        ("!" * 8 + "2" + "A", False),
    ],
)
def test_password_requirements(password: str, is_valid: bool) -> None:
    if not is_valid:
        with pytest.raises(PasswordIsNotSecure):
            vo.Password(password)
    else:
        password_vo = vo.Password(password)
        assert password_vo.value == password
