import asyncio
from pathlib import Path

from meshroom.utils import tabulate
from meshroom.model import Mode, Role, Tenant
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


@meshroom.group()
def list():
    """List products, integrations, tenants and plugs"""
    pass


@list.command(name="products")
def list_products():
    """List all products"""
    print(
        tabulate(
            sorted(model.list_products(), key=lambda x: x.name),
            headers=["Name", "Tags", "Nb integrations", "Tenants"],
            formatters={
                Tenant: lambda x: x.name,
            },
        )
    )


@list.command(name="integrations")
def list_integrations():
    """List all integrations"""
    print(
        tabulate(
            sorted(model.list_integrations(), key=lambda x: (x.product, x.target_product)),
            headers=["Product", "Target product", "Topic", "Role", "Mode", "Plugs"],
        )
    )


@list.command(name="tenants")
def list_tenants():
    """List all tenants"""
    print(
        tabulate(
            sorted(model.list_tenants(), key=lambda x: (x.product, x.name)),
            headers=["Name", "Product", "Plugs"],
        )
    )


@list.command(name="plugs")
def list_plugs():
    """List all plugs"""
    print(
        tabulate(
            sorted(model.list_plugs(), key=lambda x: (x.src_tenant, x.dst_tenant)),
            headers=["Src", "Dst", "Topic", "Mode"],
        )
    )


@meshroom.command()
@click.argument("tenant", required=False)
@click.argument("target_tenant", required=False)
@click.argument("topic", required=False)
@click.argument("mode", required=False, type=Mode)
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
@click.argument("mode", type=click.Choice(Mode.__args__), required=False)
def plug(
    src_tenant: str,
    dst_tenant: str,
    topic: str,
    mode: Mode | None = None,
):
    """Connect two products via an existing integration"""
    try:
        model.plug(src_tenant, dst_tenant, topic, mode)
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
def create_integration(
    product: str,
    target_product: str,
    topic: str,
    role: Role,
    mode: Mode,
):
    """Scaffold a new Integration"""
    model.scaffold_integration(product, target_product, topic, role, mode)


@create.command(name="product")
@click.argument("name")
def create_product(
    name: str,
):
    """Scaffold a new Product"""
    model.scaffold_product(name)


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
def add(
    product: str,
    name: str | None = None,
):
    """Add a new Tenant for a given Product"""
    try:
        tenant = model.create_tenant(product, name)
        tenant.settings = {}
        for setting in tenant.get_settings_schema():
            tenant.settings[setting.name] = click.prompt(
                f"{setting.name}",
                default=setting.default,
                hide_input=setting.secret,
            )
            tenant.save()

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
@click.option("--mode", type=Mode)
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
