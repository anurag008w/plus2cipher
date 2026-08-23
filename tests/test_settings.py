import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.settings import Settings


def _tmp_path():
    return os.path.join(tempfile.mkdtemp(), "settings.json")


def test_defaults_when_no_file():
    s = Settings.load(_tmp_path())
    assert s.theme == "dark"
    assert s.accent == "purple"
    assert s.shift == 2
    assert s.char_limit == 5000
    assert s.live_transformation is True


def test_save_and_reload_round_trip():
    path = _tmp_path()
    s = Settings.load(path)
    s.set("theme", "light")
    s.set("accent", "cyan")
    s.set("char_limit", 10000)

    s2 = Settings.load(path)
    assert s2.theme == "light"
    assert s2.accent == "cyan"
    assert s2.char_limit == 10000


def test_invalid_accent_falls_back_to_default():
    path = _tmp_path()
    with open(path, "w") as f:
        json.dump({"accent": "not-a-real-color"}, f)
    s = Settings.load(path)
    assert s.accent == "purple"


def test_invalid_shift_falls_back():
    path = _tmp_path()
    with open(path, "w") as f:
        json.dump({"shift": 999}, f)
    s = Settings.load(path)
    assert s.shift == 2


def test_corrupted_json_falls_back_to_defaults():
    path = _tmp_path()
    with open(path, "w") as f:
        f.write("{not valid json!!!")
    s = Settings.load(path)  # must not raise
    assert s.theme == "dark"


def test_unknown_key_raises():
    s = Settings.load(_tmp_path())
    try:
        s.set("totally_made_up_key", 123)
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_reset_restores_defaults():
    path = _tmp_path()
    s = Settings.load(path)
    s.set("theme", "light")
    s.reset()
    assert s.theme == "dark"
    s2 = Settings.load(path)
    assert s2.theme == "dark"


def test_get_with_default():
    s = Settings.load(_tmp_path())
    assert s.get("does_not_exist", "fallback") == "fallback"


def test_atomic_save_produces_valid_json_file():
    path = _tmp_path()
    s = Settings.load(path)
    s.set("accent", "green")
    with open(path) as f:
        data = json.load(f)
    assert data["accent"] == "green"
