import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.storage import HistoryStore


def _tmp_db():
    d = tempfile.mkdtemp()
    return os.path.join(d, "history.db")


def test_add_and_list():
    store = HistoryStore(_tmp_db())
    store.add("encode", "abc", "cde")
    store.add("decode", "cde", "abc")
    items = store.list_history()
    assert len(items) == 2
    # newest first
    assert items[0].mode == "decode"
    assert items[1].mode == "encode"


def test_favorite_toggle():
    store = HistoryStore(_tmp_db())
    rec = store.add("encode", "hi", "jk")
    assert store.list_favorites() == []
    store.set_favorite(rec.id, True)
    favs = store.list_favorites()
    assert len(favs) == 1
    assert favs[0].is_favorite is True
    store.set_favorite(rec.id, False)
    assert store.list_favorites() == []


def test_delete():
    store = HistoryStore(_tmp_db())
    rec = store.add("encode", "hi", "jk")
    store.delete(rec.id)
    assert store.list_history() == []


def test_clear_all():
    store = HistoryStore(_tmp_db())
    store.add("encode", "a", "c")
    store.add("encode", "b", "d")
    store.clear_all()
    assert store.count() == 0


def test_clear_non_favorites_preserves_favorites():
    store = HistoryStore(_tmp_db())
    r1 = store.add("encode", "a", "c")
    store.add("encode", "b", "d")
    store.set_favorite(r1.id, True)
    store.clear_non_favorites()
    remaining = store.list_history()
    assert len(remaining) == 1
    assert remaining[0].id == r1.id


def test_search_matches_input_or_output():
    store = HistoryStore(_tmp_db())
    store.add("encode", "hello world", "jgnnq yqtnf")
    store.add("encode", "goodbye", "iqqfda")
    results = store.list_history(query="hello")
    assert len(results) == 1
    results = store.list_history(query="yqtnf")
    assert len(results) == 1
    results = store.list_history(query="nomatch")
    assert results == []


def test_enforce_limit_trims_oldest_non_favorites():
    store = HistoryStore(_tmp_db())
    ids = []
    for i in range(5):
        ids.append(store.add("encode", str(i), str(i)).id)
    store.set_favorite(ids[0], True)  # protect the very first one
    store.enforce_limit(2)
    remaining = store.list_history()
    remaining_ids = {r.id for r in remaining}
    # favorite always survives regardless of limit
    assert ids[0] in remaining_ids
    assert len(remaining) <= 3  # 2 kept + 1 protected favorite


def test_export_and_import_round_trip():
    store = HistoryStore(_tmp_db())
    store.add("encode", "abc", "cde")
    store.add("decode", "cde", "abc")
    export_path = os.path.join(tempfile.mkdtemp(), "export.json")
    store.export_json(export_path)

    with open(export_path) as f:
        payload = json.load(f)
    assert len(payload["records"]) == 2

    fresh_store = HistoryStore(_tmp_db())
    imported = fresh_store.import_json(export_path)
    assert imported == 2
    assert fresh_store.count() == 2


def test_corrupted_db_recovers_gracefully():
    path = _tmp_db()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("this is not a sqlite file, totally corrupted !!")
    # Should not raise -- it should quarantine the bad file and start fresh.
    store = HistoryStore(path)
    store.add("encode", "a", "c")
    assert store.count() == 1
    assert os.path.exists(path + ".corrupt")


def test_storage_bytes_nonzero_after_write():
    path = _tmp_db()
    store = HistoryStore(path)
    store.add("encode", "a" * 500, "c" * 500)
    assert store.storage_bytes() > 0
