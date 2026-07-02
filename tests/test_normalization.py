from movie_watcher.utils import normalize_theatre_name, dedupe_preserve_order


def test_normalize_theatre_name_collapses_whitespace():
    assert normalize_theatre_name(" AGS   Villivakkam ") == "ags villivakkam"


def test_dedupe_preserve_order_keeps_first_occurrence():
    assert dedupe_preserve_order(["AGS Villivakkam", "ags   villivakkam", "PVR"]) == [
        "AGS Villivakkam",
        "PVR",
    ]
