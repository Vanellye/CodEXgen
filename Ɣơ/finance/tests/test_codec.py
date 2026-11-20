from gamma_finance.codec import calculation_terms, decode_bytes, encode_codepoints, verify_round_trip

def test_binary_round_trip_preserves_zero_bytes_and_unicode():
    payload = b"\x00A\x00" + "Ɣơ€₽".encode("utf-8")
    record = decode_bytes(payload)
    assert encode_codepoints(record.codepoints) == payload
    assert verify_round_trip(payload)
    assert record.byte_length == len(payload)

def test_zero_omission_is_only_a_derived_view():
    original = (0, 7, 0, -2)
    assert calculation_terms(original) == (7, -2)
    assert original == (0, 7, 0, -2)

def test_invalid_scalar_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        encode_codepoints([0xD800])
