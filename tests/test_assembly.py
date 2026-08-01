from django.urls import resolve


def test_message_routes_are_assembled() -> None:
    match = resolve("/api/v1/messages")
    assert match.url_name == "messages"


def test_core_health_routes_are_assembled() -> None:
    match = resolve("/api/v1/health/live")
    assert match.url_name == "liveness"
