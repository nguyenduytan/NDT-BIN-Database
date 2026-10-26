import pytest

from ndt_bin.model import normalize, merge


def test_preserves_leading_zeros_and_normalizes_aliases():
    row = normalize({"bin": "002102", "scheme": "Master Card", "type": "debit",
                     "country": "Vietnam", "issuer": "  Test   Bank ", "level": "prepaid gold"})
    assert row["bin"] == "002102"
    assert row["scheme"] == "MASTERCARD"
    assert (row["country_code"], row["country_code3"], row["country"]) == ("VN", "VNM", "Viet Nam")
    assert row["issuer"] == "TEST BANK"
    assert row["prepaid"] is True
    assert row["type"] == "DEBIT"


@pytest.mark.parametrize("value", ["1234", "12345", "1234567", "123456789", "４１１１１１", 123456, "12345x"])
def test_rejects_invalid_bins_without_guessing(value):
    with pytest.raises(ValueError):
        normalize({"bin": value})


def test_unknowns_are_null_and_unknown_type_is_not_invented():
    row = normalize({"bin": "12345678", "scheme": "N/A", "issuer": "UNKNOWN", "type": "UATP"})
    assert row["bin_length"] == 8
    assert row["scheme"] is row["issuer"] is row["type"] is row["prepaid"] is None


def test_country_code_and_name_cannot_disagree():
    with pytest.raises(ValueError, match="country"):
        normalize({"bin": "123456", "country_code": "US", "country": "Canada"})


def test_country_and_scheme_aliases():
    row = normalize({"bin": "123456", "country_code": "UK", "scheme": "CHINA UNION PAY", "type": "CHARGE CARD"})
    assert row["country_code"] == "GB"
    assert row["scheme"] == "UNIONPAY"
    assert row["type"] == "CHARGE"
    assert row["prepaid"] is None


def test_merge_selects_whole_row_and_marks_conflicts_deterministically():
    a = normalize({"bin": "123456", "issuer": "Bank A", "country_code": "US"})
    b = normalize({"bin": "123456", "issuer": "Bank B", "country_code": "CA", "type": "DEBIT"})
    observations = [("primary", 10, a), ("secondary", 20, b), ("secondary", 20, b)]
    first = merge(observations, {}, "2026-10-26")
    assert first == merge(list(reversed(observations)), {}, "2026-10-26")
    row = first[0]
    assert row["issuer"] == "BANK A"
    assert row["type"] is None  # Do not fabricate a combined record.
    assert row["source_count"] == 2
    assert "country_code" in row["conflict_fields"]
    assert row["updated_at"] == "2026-10-26"
    assert merge(observations, {"123456": row}, "2026-10-27")[0] == row


def test_eight_digit_rows_do_not_replace_their_six_digit_parent():
    rows = merge([("a", 1, normalize({"bin": b})) for b in ["123456", "12345678"]], {}, "2026-10-26")
    assert [r["bin"] for r in rows] == ["123456", "12345678"]
