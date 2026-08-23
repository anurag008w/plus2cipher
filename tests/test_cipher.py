import string
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.cipher import encode, decode, transform, apply_mode, preview_mapping


def test_encode_basic():
    assert encode("abc") == "cde"
    assert encode("A") == "C"


def test_decode_basic():
    assert decode("cde") == "abc"
    assert decode("C") == "A"


def test_wraparound():
    assert encode("y") == "a"
    assert encode("z") == "b"
    assert encode("Y") == "A"
    assert encode("Z") == "B"
    assert decode("a") == "y"
    assert decode("b") == "z"


def test_uppercase():
    assert encode("HELLO") == "JGNNQ"
    assert decode("JGNNQ") == "HELLO"


def test_lowercase():
    assert encode("hello") == "jgnnq"
    assert decode("jgnnq") == "hello"


def test_spaces():
    assert encode("a b") == "c d"
    assert encode("hello world") == "jgnnq yqtnf"


def test_numbers():
    assert encode("abc123") == "cde123"
    assert decode("cde123") == "abc123"


def test_symbols():
    assert encode("hi! @2026?") == "jk! @2026?"
    assert decode("jk! @2026?") == "hi! @2026?"


def test_multiline():
    text = "line one\nline two\tindented"
    result = encode(text)
    assert "\n" in result
    assert "\t" in result
    assert decode(result) == text


def test_round_trip():
    samples = [
        "The quick brown fox jumps over the lazy dog.",
        "what is the purpose of this cipher tool?",
        "Hello, World! 123",
        "",
        "   spaces   everywhere   ",
        "MiXeD CaSe 42!",
        string.printable,
    ]
    for text in samples:
        assert decode(encode(text)) == text


def test_reference_example():
    # Note: the original spec's worked example ("rwtwrqug") contains a typo
    # (8 letters for the 7-letter word "purpose"). This asserts the
    # mathematically correct +2 shift of the same sentence.
    assert encode("what is the purpose of this cipher tool?") == (
        "yjcv ku vjg rwtrqug qh vjku ekrjgt vqqn?"
    )


def test_reference_hello_world():
    assert encode("Hello, World! 123") == "Jgnnq, Yqtnf! 123"


def test_custom_shift():
    assert transform("abc", 5) == "fgh"
    assert transform("fgh", -5) == "abc"


def test_apply_mode():
    assert apply_mode("abc", "encode") == "cde"
    assert apply_mode("cde", "decode") == "abc"


def test_apply_mode_invalid_raises():
    try:
        apply_mode("abc", "sideways")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_preview_mapping():
    mapping = preview_mapping(2)
    assert mapping[0] == ("a", "c")
    assert mapping[-2] == ("y", "a")
    assert mapping[-1] == ("z", "b")
    assert len(mapping) == 26


def test_none_input():
    assert encode(None) == ""
    assert decode(None) == ""
