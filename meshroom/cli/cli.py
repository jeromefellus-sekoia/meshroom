from pathlib import Path
from pydantic import ValidationError

from meshroom.interaction import debug, info, error
from meshroom.utils import tabulate
from meshroom.model import Mode, Plug, ProductSetting, Role, Instance
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
        error("Directory is not a valid Meshroom project")
        exit(1)


@meshroom.command(help="Initialize a new Meshroom project")
@click.argument("path", default=".", required=False)
def init(path: str):
    """Initialize a new Meshroom project"""
    try:
        model.init_project(model.get_project_dir() / path if str(Path(path).absolute()) != path else path)
    except ValueError as e:
        error(e)
        exit(1)


@meshroom.group("list")
def _list():
    """List products, integrations, instances and plugs"""
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
                "Instances",
            ],
            formatters={
                Instance: lambda x: x.name,
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
        error(e)
        exit(1)


@_list.command(name="instances")
@click.argument("search", required=False)
@click.option("--product", "-p", help="Filter by product")
def list_instances(product: str | None = None, search: str | None = None):
    """List all instances"""
    print(
        tabulate(
            sorted(model.list_instances(product=product, search=search), key=lambda x: (x.product, x.name)),
            headers=["Name", "Product", "Plugs"],
        )
    )


@_list.command(name="plugs")
@click.argument("src_instance", required=False)
@click.argument("dst_instance", required=False)
@click.option("--topic", "-t", required=False)
@click.option("--mode", "-m", type=click.Choice(Mode.__args__), required=False)
def list_plugs(
    src_instance: str | None = None,
    dst_instance: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """List all plugs"""
    print(
        tabulate(
            sorted(model.list_plugs(src_instance=src_instance, dst_instance=dst_instance, topic=topic, mode=mode), key=lambda x: (x.src_instance, x.dst_instance)),
            headers=["Src Instance", "Dst Instance", "Topic", "Mode", "Format"],
        )
    )


@meshroom.command()
@click.argument("instance", required=False)
@click.argument("target_instance", required=False)
@click.argument("topic", required=False)
@click.argument("mode", required=False, type=click.Choice(Mode.__args__))
def up(
    instance: str | None = None,
    target_instance: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """Setup all declared Instances, a single Instance or a single Plug"""
    model.up(instance, target_instance, topic, mode)


@meshroom.command()
def down(
    instance: str | None = None,
    target_instance: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    """Unconfigure all Instances, a single Instance or a single Plug"""
    model.down(instance, target_instance, topic, mode)


@meshroom.command()
@click.argument("src_instance")
@click.argument("dst_instance")
@click.argument("topic")
@click.option("--mode", "-m", type=click.Choice(Mode.__args__), required=False)
@click.option("--format", "-f", type=str, required=False)
@click.option("--read-secret", "-s", multiple=True, help="Read a one-line secret from stdin (can be supplied multiple times)")
def plug(
    src_instance: str,
    dst_instance: str,
    topic: str,
    mode: Mode | None = None,
    format: str | None = None,
    read_secret: list[str] = [],
):
    """Connect two products via an existing integration"""
    try:
        plug = model.plug(src_instance, dst_instance, topic, mode, format)
        _configure_plug(
            plug,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
    except ValueError as e:
        error(e)
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
@click.option("--from", "template", help="Path to a templates/ subdirectory to scaffold the product from")
def create_product(
    name: str,
    template: str | None = None,
):
    """Scaffold a new Product, optionally from a template"""
    try:
        model.scaffold_product(name, template=template)
    except ValidationError as e:
        error(e)
        exit(1)


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
        error(e)
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
    """Add a new Instance for a given Product"""
    try:
        instance = model.create_instance(product, name)
        _configure_instance(
            instance,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
        info("✓ Instance created")

    except ValueError as e:
        error(e)
        exit(1)


@meshroom.command()
@click.argument("instance")
@click.option("--read-secret", "-s", multiple=True, help="Read a one-line secret from stdin (can be supplied multiple times)")
def configure(
    instance: str,
    read_secret: list[str] = [],
):
    """Reconfigure an existing Instance"""
    try:
        t = model.get_instance(instance)
        _configure_instance(
            t,
            secrets={secret: sys.stdin.readline().strip() for secret in read_secret},
        )
        info("✓ Instance configured")

    except ValueError as e:
        error(e)
        exit(1)


@meshroom.command()
@click.argument("instance")
@click.argument("product", required=False)
def remove(
    instance: str,
    product: str | None = None,
):
    """Remove a Instance for a given Product"""
    model.delete_instance(instance, product)


@meshroom.command()
@click.argument("src_instance")
@click.argument("dst_instance")
@click.argument("topic")
@click.option("--mode", type=click.Choice(Mode.__args__))
def unplug(
    src_instance: str,
    dst_instance: str,
    topic: str,
    mode: Mode | None = None,
):
    """Disconnect an existing Plug between two Instances"""
    model.unplug(src_instance, dst_instance, topic, mode)


@meshroom.command()
@click.argument("topic")
@click.argument("instance")
@click.argument("dst_instance", required=False)
@click.option("--mode", type=click.Choice(Mode.__args__))
def watch(
    topic: str,
    instance: str,
    dst_instance: str | None,
    mode: Mode | None,
):
    """Inspect data flowing through a Plug or a Instance"""
    try:
        for msg in model.watch(instance, dst_instance, topic, mode):
            print(msg)
    except ValueError as e:
        error(e)
        exit(1)
    except KeyboardInterrupt:
        ...


@meshroom.command()
@click.argument("topic")
@click.argument("instance")
@click.argument("dst_instance", required=False)
@click.option("--mode", type=click.Choice(Mode.__args__))
def produce(
    topic: str,
    instance: str,
    dst_instance: str | None = None,
    mode: Mode | None = None,
):
    """Produce data through a Plug or to a Instance"""
    try:
        debug("Waiting for events on stdandard input...\n")
        for line in sys.stdin:
            print(model.produce(instance, dst_instance, topic, data=line.strip(), mode=mode))
    except ValueError as e:
        error(e)
        exit(1)


@meshroom.command()
@click.argument("topic")
@click.argument("instance")
@click.argument("dst_instance", required=False)
@click.option("--mode", type=click.Choice(Mode.__args__))
@click.option("--param", "-p", multiple=True)
def execute(
    topic: str,
    instance: str,
    dst_instance: str | None = None,
    mode: Mode | None = None,
    param: list[str] = [],
):
    """Execute an executor exposed by a Plug's or a Instance's topic"""
    try:
        print(
            model.execute(
                instance,
                dst_instance,
                topic,
                data={k: v for k, v in (p.split("=") for p in param)},
                mode=mode,
            )
        )
    except ValueError as e:
        error(e)
        exit(1)


@meshroom.command()
@click.argument("topic")
@click.argument("instance")
@click.argument("dst_instance", required=False)
@click.option("--mode", type=click.Choice(Mode.__args__))
@click.option("--param", "-p", multiple=True)
def trigger(
    topic: str,
    instance: str,
    dst_instance: str | None = None,
    mode: Mode | None = None,
    param: list[str] = [],
):
    """Trigger an trigger exposed by a Plug's or a Instance's topic"""
    try:
        print(
            model.trigger(
                instance,
                dst_instance,
                topic,
                data={k: v for k, v in (p.split("=") for p in param)},
                mode=mode,
            )
        )
    except ValueError as e:
        error(e)
        exit(1)


@meshroom.command()
@click.argument("product", required=False)
@click.argument("target_product", required=False)
@click.argument("topic", required=False)
@click.argument("role", type=click.Choice(Role.__args__), required=False)
@click.option("--mode", "-m", type=click.Choice(Mode.__args__))
@click.option("--format", "-f")
def publish(
    product: str,
    target_product: str | None = None,
    topic: str | None = None,
    role: Role | None = None,
    mode: Mode | None = None,
    format: str | None = None,
):
    """
    Publish a specific integration, a given product's integrations or all integrations at once
    according to the @publish decorators eventually set in the integrations' code
    """
    try:
        model.publish(product, target_product, topic, role, mode, format)
    except ValueError as e:
        error(e)
        exit(1)


def _configure_instance(t: Instance, secrets: dict[str, str] = {}):
    t.settings = t.settings or {}
    for setting in t.get_settings_schema():
        if setting.secret:
            if setting.name in secrets:
                t.set_secret(setting.name, secrets[setting.name])
            else:
                _configure_secret(t, setting)
        elif sys.stdin.isatty():  # only prompt if stdin is a tty
            t.settings[setting.name] = _prompt_setting(setting, default=t.settings.get(setting.name))
            t.save()


def _configure_plug(p: Plug, secrets: dict[str, str] = {}):
    for end, setting in p.get_unconfigured_settings():
        if setting.secret:
            if setting.name in secrets:
                p.set_secret(setting.name, secrets[setting.name])
            else:
                _configure_secret(p, setting)
        elif sys.stdin.isatty():  # only prompt if stdin is a tty
            if end == "src":
                p.src_config[setting.name] = _prompt_setting(setting, default=p.src_config.get(setting.name))
                p.save()
            else:
                p.dst_config[setting.name] = _prompt_setting(setting, default=p.dst_config.get(setting.name))
                p.save()


def _configure_secret(t: Instance | Plug, setting: ProductSetting):
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
