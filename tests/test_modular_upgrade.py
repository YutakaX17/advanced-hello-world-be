import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_fresh_modular_install_persists_a_message() -> None:
    response = APIClient().post(
        reverse("advanced_hello_world_messages:messages"),
        {"text": "Fresh modular install"},
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["text"] == "Fresh modular install"


@pytest.mark.django_db(transaction=True)
def test_existing_core_message_survives_modular_upgrade() -> None:
    executor = MigrationExecutor(connection)
    old_target = [("advanced_hello_world_core", "0001_initial")]
    executor.migrate(old_target)
    old_apps = executor.loader.project_state(old_target).apps
    old_message = old_apps.get_model("advanced_hello_world_core", "Message")
    existing = old_message.objects.create(text="Created before extraction")

    executor = MigrationExecutor(connection)
    latest_targets = executor.loader.graph.leaf_nodes()
    executor.migrate(latest_targets)
    current_apps = executor.loader.project_state(latest_targets).apps
    current_message = current_apps.get_model("advanced_hello_world_messages", "Message")

    migrated = current_message.objects.get(pk=existing.pk)
    assert migrated.text == "Created before extraction"
