from django.urls import resolve


def test_core_routes_are_assembled() -> None:
    match = resolve("/api/v1/messages")
    assert match.url_name == "messages"
