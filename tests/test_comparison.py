from movie_watcher.watcher import compare_theatres


def test_compare_theatres_detects_added_and_removed():
    change = compare_theatres(["AGS Villivakkam", "PVR"], ["AGS Villivakkam", "S2"])
    assert change.added == ["PVR"]
    assert change.removed == ["S2"]
