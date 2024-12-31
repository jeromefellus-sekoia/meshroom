import asyncio
from pathlib import Path
import re

from meshroom.utils import tabulate
from meshroom.model import Mode, Plug, ProductSetting, Role, Tenant
import click
from meshroom import model
import sys


@click.group()
@click.option("-p", "--path", default=".", help="Path to the meshroom project directory")
def meshroom(path):
    """Meshroom - The composable SOC assistant"""
    model.set_project_dir(path)

    # skip validation for init command
    if click.get_current_context().invoked_subcommand == "init":
        return

    if not model.validate_meshroom_project(path):
        click.echo("Directory is not a valid Meshroom project")
        exit(1)


@meshroom.command(help="Initialize a new Meshroom project")
@click.argument("path", default=".", required=False)
def init(path: str):
    """Initialize a new Meshroom project"""
    try:
        model.init_project(model.get_project_dir() / path if str(Path(path).absolute()) != path else path)
    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.group("list")
def _list():
    """List products, integrations, tenants and plugs"""
    pass


@_list.command(name="products")
@click.option("--wide", "-w", is_flag=True, help="Show more details (consumes, produces, ...)")
@click.argument("search", required=False)
def list_products(wide: bool = False, search: str | None = None):
    """List all products"""

    wide_headers = {}
    if wide:
        wide_headers = [
            {"Consumes": lambda x: x.list_capabilities("consumer")},
            {"Produces": lambda x: x.list_capabilities("producer")},
        ]

    print(
        tabulate(
            sorted(model.list_products(search=search), key=lambda x: x.name),
            headers=[
                "Name",
                "Tags",
                *wide_headers,
                "Nb integrations",
                "Tenants",
            ],
            formatters={
                Tenant: lambda x: x.name,
            },
        )
    )


@_list.command(name="integrations")
@click.argument("product", required=False)
@click.argument("target_product", required=False)
@click.option("--topic", "-t", help="Filter by topic")
def list_integrations(
    product: str | None = None,
    target_product: str | None = None,
    topic: str | None = None,
):
    """List all integrations"""
    try:
        print(
            tabulate(
                sorted(model.list_integrations(product=product, target_product=target_product, topic=topic), key=lambda x: (x.product, x.target_product)),
                headers=["Product", {"3rd-party product": "target_product"}, "Topic", "Role", "Mode", "Plugs"],
            )
        )
    except ValueError as e:
        click.echo(e)
        exit(1)


@_list.command(name="tenants")
@click.argument("search", required=False)
@click.option("--product", "-p", help="Filter by product")
def list_tenants(product: str | None = None, search: str | None = None):
    """List all tenants"""
    print(
        tabulate(
            sorted(model.list_tenants(product=product, search=search), key=lambda x: (x.product, x.name)),
            headers=["Name", "Product", "Plugs"],
        )
    )


@_list.command(name="plugs")
@click.argument("src_tenant", required=False)
@click.argument("dst_tenant", required=False)
@click.option("--topic", "-t", required=False)
@click.option("--mode", "-m", type=click.Choice(Mode.__args__), required=False)
def list_plugs(
    src_tenant: str | None = None,
    dst_tenant: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """List all plugs"""
    print(
        tabulate(
            sorted(model.list_plugs(src_tenant=src_tenant, dst_tenant=dst_tenant, topic=topic, mode=mode), key=lambda x: (x.src_tenant, x.dst_tenant)),
            headers=["Src Tenant", "Dst Tenant", "Topic", "Mode", "Format"],
        )
    )


@meshroom.command()
@click.argument("tenant", required=False)
@click.argument("target_tenant", required=False)
@click.argument("topic", required=False)
@click.argument("mode", required=False, type=click.Choice(Mode.__args__))
def up(
    tenant: str | None = None,
    target_tenant: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """Setup all declared Tenants, a single Tenant or a single Plug"""
    model.up(tenant, target_tenant, topic, mode)


@meshroom.command()
def down(
    tenant: str | None = None,
    target_tenant: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """Unconfigure all Tenants, a single Tenant or a single Plug"""
    model.down(tenant, target_tenant, topic, mode)


@meshroom.command()
@click.argument("src_tenant")
@click.argument("dst_tenant")
@click.argument("topic")
@click.option("--mode", "-m", type=click.Choice(Mode.__args__), required=False)
@click.option("--format", "-f", type=str, required=False)
@click.option("--read-secret", "-s", multiple=True, help="Read a one-line secret from stdin (can be supplied multiple times)")
def plug(
    src_tenant: str,
    dst_tenant: str,
    topic: str,
    mode: Mode | None = None,
    format: str | None = None,
    read_secret: list[str] = [],
):
    """Connect two products via an existing integration"""
    try:
        plug = model.plug(src_tenant, dst_tenant, topic, mode, format)
        _configure_plug(
            plug,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.group()
def create():
    """Create a new product or integration"""
    pass


@create.command(name="integration")
@click.argument("product")
@click.argument("target_product")
@click.argument("topic")
@click.argument("role", type=click.Choice(Role.__args__))
@click.option("--mode", type=click.Choice(Mode.__args__), default="push")
@click.option("--format", "-f")
def create_integration(
    product: str,
    target_product: str,
    topic: str,
    role: Role,
    mode: Mode,
    format: str | None = None,
):
    """Scaffold a new Integration"""
    # First scaffold the products capabilities if it doesn't exist
    model.scaffold_capability(product, topic, role, mode, format)
    model.scaffold_capability(
        target_product,
        topic,
        # Create the complementary capability
        {"consumer": "producer", "producer": "consumer", "executor": "trigger", "trigger": "executor"}[role],
        mode,
        format,
    )
    # Then create the integration itself
    model.scaffold_integration(product, target_product, topic, role, mode, format)


@create.command(name="product")
@click.argument("name")
def create_product(
    name: str,
):
    """Scaffold a new Product"""
    model.scaffold_product(name)


@create.command(name="capability")
@click.argument("product")
@click.argument("topic")
@click.argument("role", type=click.Choice(Role.__args__))
@click.option("--mode", "-m", type=click.Choice(Mode.__args__), default="push")
@click.option("--format", "-f")
def create_capability(
    product: str,
    topic: str,
    role: Role,
    mode: Mode,
    format: str | None = None,
):
    """Scaffold a new product Capability"""
    model.scaffold_capability(product, topic, role, mode, format)


@meshroom.command()
@click.argument("product")
def pull(
    product: str,
):
    """Pull a product's SDK from its repository"""
    try:
        model.get_product(product).pull()
    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.command()
@click.argument("product")
@click.argument("name", required=False)
@click.option("--read-secret", "-s", multiple=True, help="Read a one-line secret from stdin (can be supplied multiple times)")
def add(
    product: str,
    name: str | None = None,
    read_secret: list[str] = [],
):
    """Add a new Tenant for a given Product"""
    try:
        tenant = model.create_tenant(product, name)
        _configure_tenant(
            tenant,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
        print("✓ Tenant created")

    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.command()
@click.argument("tenant")
@click.option("--read-secret", "-s", multiple=True, help="Read a one-line secret from stdin (can be supplied multiple times)")
def configure(
    tenant: str,
    read_secret: list[str] = [],
):
    """Reconfigure an existing Tenant"""
    try:
        t = model.get_tenant(tenant)
        _configure_tenant(
            t,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
        print("✓ Tenant configured")

    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.command()
@click.argument("tenant")
@click.argument("product", required=False)
def remove(
    tenant: str,
    product: str | None = None,
):
    """Remove a Tenant for a given Product"""
    model.delete_tenant(tenant, product)


@meshroom.command()
@click.argument("src_tenant")
@click.argument("dst_tenant")
@click.argument("topic")
@click.option("--mode", type=click.Choice(Mode.__args__))
def unplug(
    src_tenant: str,
    dst_tenant: str,
    topic: str,
    mode: Mode | None = None,
):
    """Disconnect an existing Plug between two Tenants"""
    model.unplug(src_tenant, dst_tenant, topic, mode)


@meshroom.command()
@click.argument("src_tenant")
@click.argument("dst_tenant")
@click.argument("topic")
@click.option("--mode", type=click.Choice(Mode.__args__), default="push")
def watch(
    src_tenant: str,
    dst_tenant: str,
    topic: str,
    mode: Mode,
):
    """Inspect data flowing through a Plug"""
    try:
        asyncio.run(model.watch(src_tenant, dst_tenant, topic, mode))
    except ValueError as e:
        click.echo(e)
        exit(1)


@meshroom.command()
@click.argument("src_tenant")
@click.argument("dst_tenant")
@click.argument("topic")
@click.option("--mode", type=click.Choice(Mode.__args__), default="push")
def emulate(
    src_tenant: str,
    dst_tenant: str,
    topic: str,
    mode: Mode,
):
    """Emulate data flowing through a Plug"""
    try:
        for line in sys.stdin:
            model.emulate(src_tenant, dst_tenant, topic, mode, line.strip())
    except ValueError as e:
        click.echo(e)
        exit(1)


def _configure_tenant(t: Tenant, secrets: dict[str, str] = {}):
    t.settings = t.settings or {}
    for setting in t.get_settings_schema():
        if setting.secret:
            if setting.name in secrets:
                t.set_secret(setting.name, secrets[setting.name])
            else:
                _configure_secret(t, setting)
        else:
            t.settings[setting.name] = _prompt_setting(setting, default=t.settings.get(setting.name))
            t.save()


def _configure_plug(p: Plug, secrets: dict[str, str] = {}):
    for end, setting in p.get_unconfigured_settings():
        if setting.secret:
            if setting.name in secrets:
                p.set_secret(setting.name, secrets[setting.name])
            else:
                _configure_secret(p, setting)
        elif end == "src":
            p.src_config[setting.name] = _prompt_setting(setting, default=p.src_config.get(setting.name))
            p.save()
        else:
            p.dst_config[setting.name] = _prompt_setting(setting, default=p.dst_config.get(setting.name))
            p.save()


def _configure_secret(t: Tenant | Plug, setting: ProductSetting):
    title = f"{setting.name} (secret)"
    if t.get_secret(setting.name):
        title = f"{setting.name} (secret, press Enter to keep current value)"
    t.set_secret(setting.name, _prompt_setting(setting, title=title, default=t.settings.get(setting.name)))
    t.save()


def _prompt_setting(setting: ProductSetting, title: str | None = None, default=None):
    if setting.secret:
        title = title or f"{setting.name} (secret)"
        return click.prompt(
            title,
            default=default,
            show_default=False,
            hide_input=True,
        )

    else:
        title = title or setting.name
        if setting.type == "boolean":
            return click.confirm(
                setting.name,
                default=default or setting.default,
            )

        if setting.type == "array":
            print(title + "[] (enter blank line to finish)")
            return list(iter(lambda: click.prompt("> ", default=""), ""))

        if setting.type == "object":
            print(title)
            print("-" * len(title))
            out = {prop.name: _prompt_setting(prop, default=default.get(prop.name) if default else None) for prop in setting.properties}
            print()
            return out

        x = click.prompt(
            setting.name,
            default=default or setting.default,
        )

        if setting.type == "number":
            return float(x)
        if setting.type == "integer":
            return int(x)
        return x
