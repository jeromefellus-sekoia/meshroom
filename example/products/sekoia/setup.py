from meshroom.decorators import setup_consumer, teardown_consumer
from meshroom.model import Integration, Plug, Tenant
from .api import SekoiaAPI


@setup_consumer("events", order="first")
def create_intake_key(integration: Integration, plug: Plug, tenant: Tenant):
    """Create an intake key to consume events"""

    if intake_key := plug.get_secret("intake_key"):
        print("🚫 Intake key already exists")
        return intake_key

    api = SekoiaAPI(
        tenant.settings.get("region", "fra1"),
        tenant.get_secret("API_KEY"),
    )

    intake_name = integration.target_product.replace("_", " ")

    # Get or create main entity (because we need one to create an intake key)
    entity_uuid = api.get_or_create_main_entity()["uuid"]

    # Pull intakes require an automation connector
    if integration.mode == "pull":
        # Find or create a suitable module configuration
        module_configuration = plug.dst_config.get("module_configuration") or {}
        connector_configuration = plug.dst_config.get("connector_configuration") or {}
        module_configuration_uuid = api.get_or_create_module_configuration(
            integration.automation_module_uuid,
            "Meshroom",
            module_configuration,
        )["uuid"]

        # Create the pull intake along with the automation connector
        intake = api.create_intake_key(
            entity_uuid,
            integration.intake_format_uuid,
            intake_name,
            connector_configuration=connector_configuration,
            connector_module_configuration_uuid=module_configuration_uuid,
        )
    else:
        # Create the push intake
        intake = api.create_intake_key(
            entity_uuid,
            integration.intake_format_uuid,
            intake_name,
        )

    # Securely store the intake key
    plug.set_secret("intake_key", intake["intake_key"])

    print(f"✓ Intake {intake_name} created")


@teardown_consumer("events")
def delete_intake_key(integration: Integration, plug: Plug, tenant: Tenant):
    """Delete the intake key when the plug is torn down"""
    api = SekoiaAPI(
        tenant.settings.get("region", "fra1"),
        tenant.get_secret("API_KEY"),
    )

    intake_name = integration.target_product.replace("_", " ")

    intake_keys = api.get_intake_keys(intake_name, integration.intake_format_uuid)
    for intake_key in intake_keys:
        api.delete_intake_key(intake_key["uuid"])
        print(f"✓ Intake {intake_key['name']} deleted")

    plug.delete_secret("intake_key")
