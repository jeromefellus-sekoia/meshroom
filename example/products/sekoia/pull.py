from ast import In
import json
import logging
from pathlib import Path
import re
from meshroom.model import Integration, Plug, ProductSetting, create_product, get_integration, get_product
from meshroom.utils import cp_rf, git_pull
import yaml


def pull_automation_library(path: Path):
    """Pull automation library from Sekoia's public automation-library repo"""
    sekoia = get_product("sekoia")
    path = path / "automation-library"
    git_pull("https://github.com/SEKOIA-IO/automation-library.git", path)

    # Collect all automation library manifests
    for manifest in path.rglob("manifest.json"):
        module = manifest.parent

        with open(manifest, "r") as file:
            manifest_data = json.load(file)

        product_name = re.sub(r"[-\s]+", "_", manifest_data["slug"]).lower()

        # Lazily create products if needed
        try:
            product = get_product(product_name)
        except ValueError:
            print("Create product", product_name)
            product = create_product(product_name)

            if description := manifest_data.get("description"):
                product.description = description

            product.settings = parse_module_configuration(manifest_data.get("configuration"))

            for fmt in ("svg", "png", "jpg"):
                if (module / f"logo.{fmt}").is_file():
                    product.set_logo(module / f"logo.{fmt}")
                    break

            product.save()

        # Copy automation files to the integration folder
        integration_path = sekoia.path / "integrations" / product_name / "dist" / "automation"
        cp_rf(module, integration_path)


def parse_module_configuration(configuration: dict | None = None):
    """Convert an automation module configuration JSON schema to a list of ProductSetting objects"""
    out = []
    if not configuration:
        return out

    if configuration.get("type") not in (None, "object", "array"):
        if configuration.get("name"):
            return ProductSetting(
                name=configuration["name"],
                type=configuration["type"],
                description=configuration.get("description", ""),
                default=configuration.get("default"),
                required=configuration.get("required", False),
                secret=configuration.get("secret", False),
            )
        return configuration["type"]

    for k, v in configuration.get("properties", {}).items():
        is_secret = k in configuration.get("secrets", [])
        is_required = k in configuration.get("required", [])
        try:
            out.append(
                ProductSetting(
                    name=k,
                    type=v.get("type", "string"),
                    description=v.get("description", ""),
                    default=v.get("default"),
                    required=is_required or v.get("required", False),
                    secret=is_secret or v.get("secret", False),
                    items=parse_module_configuration(v.get("items", {})) or [],
                    properties=parse_module_configuration({"name": k, **v}) if v.get("type") == "object" else [],
                )
            )
        except ValueError:
            logging.warning(f"WARNING: Error creating product setting for\n\n{configuration}\n\n{k}:{v}", exc_info=True)

    return out


def get_automation_module(path: Path, uuid: str):
    """Get automation module from Sekoia's public automation-library repo given its UUID"""
    path = path / "automation-library"
    for manifest in path.rglob("manifest.json"):
        with open(manifest, "r") as file:
            manifest_data = json.load(file)
            if manifest_data.get("uuid") == uuid:
                return manifest.parent
    return None


def pull_intake_formats(path: Path):
    """Pull intake formats from Sekoia's public intakes repo"""
    sekoia = get_product("sekoia")
    path = path / "intake-formats"
    git_pull("https://github.com/SEKOIA-IO/intake-formats.git", path)

    # Collect all intake formats manifests
    for manifest in path.rglob("_meta/manifest.yml"):
        module_manifest = manifest.parent.parent.parent / "_meta" / "manifest.yml"

        # Skip the utils/ folder
        if manifest.is_relative_to(path / "utils"):
            continue

        # Intake manifests are expected to be nested under a module folder
        if not module_manifest.is_file():
            continue

        # Intakes without an ingest parser.yml manifest aren't considered valid
        if not (manifest.parent.parent / "ingest" / "parser.yml").is_file():
            continue

        with open(module_manifest, "r") as file:
            module_manifest_data = yaml.safe_load(file)

        with open(manifest, "r") as file:
            manifest_data = yaml.safe_load(file)
            product_name = re.sub(r"[-\s]+", "_", manifest_data["slug"]).lower()

        uuid = manifest_data.get("uuid")

        # Map the intake format to the corresponding automation module if any
        # (automation library being the prefered source of truth for the product name)
        # If no automation module is found, the product name is derived from the intake format's slug
        if manifest_data.get("automation_module_uuid") and (automation_module := get_automation_module(path, manifest_data["automation_module_uuid"])):
            with open(automation_module / "manifest.json", "r") as file:
                product_name = re.sub(r"[-\s]+", "_", json.load(file)["slug"]).lower()

        # Intakes with an automation connector UUID are pull mode
        mode = "pull" if manifest_data.get("automation_connector_uuid") else "push"

        # Lazily create products if needed
        try:
            product = get_product(product_name)
        except ValueError:
            print("Create product", product_name)
            product = create_product(product_name)

            if description := manifest_data.get("description"):
                product.description = description
            if vendor := module_manifest_data.get("name"):
                product.vendor = vendor

            for fmt in ("svg", "png", "jpg"):
                if (manifest.parent / f"logo.{fmt}").is_file():
                    product.set_logo(manifest.parent / f"logo.{fmt}")
                    break

            product.save()

        # Copy intake format files to the integration folder
        i = Integration(product="sekoia", target_product=product_name, topic="events", role="consumer", mode=mode)
        cp_rf(manifest.parent.parent, i.path / "dist" / "intake-format")

        # Create the Sekoia end of the integration
        i.mode = mode
        i.documentation_url = f"https://docs.sekoia.io/operation_center/integration_catalog/uuid/{uuid}"
        i.settings["intake_format_uuid"] = uuid

        if mode == "pull":
            # Setting up a pull integration involves setting up the automation connector
            i.add_setup_step("Create Sekoia.io intake key", step_create_intake_key, order="first")
            i.add_setup_step("Create connector playbook", step_create_connector, order="last")
        else:
            # Push intakes require manual setup instructions for the 3rd party
            i.documentation_url = f"https://docs.sekoia.io/operation_center/integration_catalog/uuid/{uuid}/#instructions-on-the-3rd-party-solution"
            i.add_setup_step("Create Sekoia.io intake key", step_create_intake_key, order="first")

            # Create the 3rd-party setup if it doesn't exist yet
            if not get_integration(product_name, "sekoia", "events", "producer", mode):
                dst = Integration(product=product_name, target_product="sekoia", topic="events", role="producer", mode=mode)
                dst.documentation_url = f"https://docs.sekoia.io/operation_center/integration_catalog/uuid/{uuid}/#instructions-on-the-3rd-party-solution"
                dst.add_setup_step("Follow syslog forwarding instructions", syslog_forwarding_instructions)
                dst.save()

        i.save()


# Setup steps


def step_create_intake_key(integration: Integration, plug: Plug):
    if not plug.get_secret("intake_key"):
        intake_format_uuid = integration.settings["intake_format_uuid"]
        intake_name = integration.target_product
        intake_key = create_intake_key(intake_format_uuid, intake_name)
        plug.set_secret("intake_key", intake_key)


def step_create_connector(integration: Integration, plug: Plug):
    print("SETUP CONNECTOR")
    # TODO setup connector


def syslog_forwarding_instructions(integration: Integration, plug: Plug):
    print(f"To setup {plug}, please follow {integration.documentation_url}")
    print("You'll need your intake key :", plug.get_secret("intake_key"))
    input("Press Enter when done")

    plug.save()


def create_intake_key(intake_format_uuid: str, name: str, default_entity="Main entity"):
    # TODO create intake key
    entity_uuid = get_or_create_main_entity(default_entity)

    return "blabla"


def get_or_create_main_entity(default_name: str):
    # TODO get first entity or create one
    return "blabla"
