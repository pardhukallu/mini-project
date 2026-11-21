import pytest
from pydantic import ValidationError

from app.schemas.breach import EmailBreachRequest


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("user@example.com", "user@example.com"),
        ("USER@EXAMPLE.COM", "user@example.com"),
        ("  user@example.com  ", "user@example.com"),
        ("name+tag@sub.example.co.uk", "name+tag@sub.example.co.uk"),
        ("user@example.io", "user@example.io"),
    ],
)
def test_valid_emails_are_normalized(raw, expected):
    assert str(EmailBreachRequest(email=raw).email) == expected


def test_idn_domain_is_accepted():
    # EmailStr normalizes punycode domains to their Unicode form.
    normalized = str(EmailBreachRequest(email="user@example.xn--p1ai").email)
    assert normalized.startswith("user@example.")
    assert normalized != "user@example.xn--p1ai"


@pytest.mark.parametrize(
    "raw",
    [
        "wrongmail",
        "not-an-email",
        "user@example",
        "user@localhost",
        ".user@example.com",
        "user..name@example.com",
        "user@example..com",
        "user@-example.com",
        "user@example-.com",
        "user@b.c",
        "user@example.c",
        "user@example.123",
    ],
)
def test_malformed_emails_are_rejected(raw):
    with pytest.raises(ValidationError):
        EmailBreachRequest(email=raw)
