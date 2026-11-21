import pytest

from app.services.xposedornot import _extract_breach_names


def test_not_found_payload_returns_no_records():
    assert _extract_breach_names({"Error": "Not found", "email": None}) == []


def test_empty_breach_payload_returns_no_records():
    assert _extract_breach_names({"breaches": []}) == []


def test_only_names_in_api_payload_are_returned():
    assert _extract_breach_names({"breaches": [["Breach One", "Breach Two"]]}) == [
        {"name": "Breach One"},
        {"name": "Breach Two"},
    ]


def test_duplicate_names_are_removed_without_adding_metadata():
    records = _extract_breach_names({"breaches": [["Breach One", "Breach One"]]})
    assert records == [{"name": "Breach One"}]
    assert set(records[0]) == {"name"}


def test_unexpected_response_shape_is_not_treated_as_clean():
    with pytest.raises(ValueError):
        _extract_breach_names({"unexpected": "payload"})
