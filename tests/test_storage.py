from movie_watcher.storage import load_theatres, save_theatres, backup_file, restore_file


def test_save_and_load_theatres(tmp_path):
    path = tmp_path / "theatres.json"
    save_theatres(path, ["AGS", "PVR"])
    assert load_theatres(path) == ["AGS", "PVR"]


def test_backup_and_restore_file(tmp_path):
    path = tmp_path / "theatres.json"
    path.write_text('{"theatres":["AGS"]}', encoding="utf-8")
    backup = backup_file(path)
    path.write_text('{"theatres":["PVR"]}', encoding="utf-8")
    restore_file(path, backup)
    assert path.read_text(encoding="utf-8") == '{"theatres":["AGS"]}'
