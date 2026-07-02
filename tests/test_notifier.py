from movie_watcher.notifier import format_notification


def test_notification_formatting_single_and_multiple():
    url = "https://in.bookmyshow.com/movies/chennai/gatta-kusthi-2/buytickets/ET00502802/20260703"
    single = format_notification(["AGS Villivakkam"], click_url=url)
    multiple = format_notification(["AGS Villivakkam", "PVR VR Mall"], click_url=url)
    assert single.title == "Gatta Kusthi 2"
    assert "New theatre added!" in single.body
    assert "New theatres added!" in multiple.body
    assert "🏢 AGS Villivakkam" in multiple.body
