from movie_watcher.parser import extract_theatre_names_from_text, extract_from_candidates


def test_extract_theatre_names_from_html_like_text():
    text = '<div data-name="AGS Villivakkam"></div><script>{"venueName":"PVR VR Mall"}</script>'
    assert extract_theatre_names_from_text(text) == ["AGS Villivakkam", "PVR VR Mall"]


def test_extract_from_candidates_removes_duplicates():
    assert extract_from_candidates(["AGS", "AGS ", "PVR"]) == ["AGS", "PVR"]
