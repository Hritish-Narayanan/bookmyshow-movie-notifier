from movie_watcher.storage import save_theatres, load_theatres, backup_file, restore_file
from movie_watcher.watcher import compare_theatres


def test_fake_theatre_insertion_and_restore(tmp_path):
    path = tmp_path / "theatres.json"
    save_theatres(path, [{"venueName": "AGS", "theatreId": "ags-1"}])
    original = backup_file(path)
    current = load_theatres(path)
    injected = current + [
        {"venueName": "Fake Theatre Alpha", "theatreId": "fake-alpha"},
        {"venueName": "Fake Theatre Beta", "theatreId": "fake-beta"},
    ]
    save_theatres(path, injected)
    change = compare_theatres(injected, current)
    assert change.added == ["Fake Theatre Alpha", "Fake Theatre Beta"]
    restore_file(path, original)
    assert load_theatres(path) == [{"venueName": "AGS", "theatreId": "ags-1"}]


def test_remove_mode_simulates_removed_theatre(tmp_path):
    path = tmp_path / "theatres.json"
    save_theatres(
        path,
        [
            {"venueName": "AGS", "theatreId": "ags-1"},
            {"venueName": "PVR", "theatreId": "pvr-1"},
        ],
    )
    current = load_theatres(path)
    injected = current[:-1]
    change = compare_theatres(injected, current)
    assert change.removed == ["PVR"]
