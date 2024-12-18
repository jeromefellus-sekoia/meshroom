import asyncio
import inspect
import logging
from pathlib import Path
from typing import Any, Callable, Generator, Literal
from pydantic import BaseModel, ConfigDict
import yaml
import shutil

from meshroom import secrets
from meshroom.ast import AST
from meshroom.utils import import_module, list_functions_from_module

Role = Literal["consumer", "producer", "trigger", "executor"]
Mode = Literal["push", "pull"]

PROJECT_DIR = Path(".")


class Model(BaseModel):
    """Base model for all Meshroom models"""

    model_config = ConfigDict(
        json_encoders={
            set: list,
        }
    )

    def model_dump(self, *args, **kw):
        kw["exclude_defaults"] = True
        kw["exclude_none"] = True
        return super().model_dump(*args, **kw)


class Consumer(Model):
    format: str | None = None
    mode: Mode = "push"


class Producer(Model):
    format: str | None = None
    mode: Mode = "push"


class Capability(Model):
    """
    Definition of a Product's generic consumer/producer capability
    """

    topic: str
    role: Role
    mode: Mode = "push"
    format: str | None = None

    @staticmethod
    def consumer(topic: str, consumer: Consumer):
        """Create a consumer capability"""
        return Capability(topic=topic, role="consumer", mode=consumer.mode, format=consumer.format)

    @staticmethod
    def producer(topic: str, producer: Producer):
        """Create a producer capability"""
        return Capability(topic=topic, role="producer", mode=producer.mode, format=producer.format)

    def __hash__(self):
        return (self.topic, self.role, self.mode, self.format).__hash__()

    def __eq__(self, value: "Capability"):
        return self.topic == value.topic and self.role == value.role and self.mode == value.mode and self.format == value.format

    def matches(self, capability: "Capability"):
        """Check if this capability matches a complementary capability (e.g., consumer/producer)"""
        return (
            self.topic == capability.topic
            and (sorted((self.role, capability.role)) in (["consumer", "producer"], ["executor", "trigger"]))
            and self.mode == capability.mode
            and (self.format == capability.format or None in (self.format, capability.format))
        )

    def __str__(self):
        x = []
        if self.mode not in ("push", None):
            x.append(self.mode)
        if self.format is not None:
            x.append(self.format)
        out = self.topic
        if x:
            out += f" ({' '.join(x)})"
        return out

    def __repr__(self):
        return str(self)


class Product(Model):
    """
    Definition of a product's capabilities
    :name: The name of the product, which is also the directory name under /products
    :tags: A set of tags that describe the product's functional scopes
    """

    name: str
    description: str = ""
    vendor: str = ""
    tags: set[str] = set()
    settings: list["ProductSetting"] = []
    consumes: dict[str, list[Consumer]] = {}
    produces: dict[str, list[Producer]] = {}

    @staticmethod
    def load(path: Path):
        # Optionally read the definition.yaml file
        path = path_in_project(path)
        definition = {}
        if (path / "definition.yaml").is_file():
            with open(path / "definition.yaml") as f:
                definition = yaml.safe_load(f)
        definition["name"] = path.name
        return Product.model_validate(definition)

    def save(self):
        definition = self.model_dump()
        self.path.mkdir(parents=True, exist_ok=True)
        with open(self.path / "definition.yaml", "w") as f:
            yaml.safe_dump(definition, f)
        return self

    def update(self, description: str | None = None, tags: set[str] | None = None):
        if description is not None:
            self.description = description
        if tags is not None:
            self.tags = set(tags)
        return self.save()

    def set_logo(self, image_path: Path | str):
        image_path = Path(image_path)
        return shutil.copy(image_path, self.path / f"logo{image_path.suffix}")

    @property
    def path(self):
        return path_in_project(PROJECT_DIR / "products" / self.name)

    @property
    def nb_integrations(self):
        return len(list(list_integrations(product=self.name)))

    @property
    def tenants(self):
        return list(list_tenants(self.name))

    def add_consumer_setup_step(
        self,
        title: str,
        func: Callable | str,
        topic: str,
        mode: Mode = "push",
        order: str | None = None,
    ):
        """
        Append a generic setup step to the product's setup.py
        to setup a consumer for the given topic
        """
        import meshroom.decorators

        ast = AST(self.path / "setup.py")
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.setup_consumer,
                order=order,
                topic=topic,
                mode=mode,
                title=title,
            )
        ast.save()
        return self

    def add_producer_setup_step(
        self,
        title: str,
        func: Callable | str,
        topic: str,
        mode: Mode = "push",
        order: str | None = None,
    ):
        """
        Append a generic setup step to the product's setup.py
        to setup a producer for the given topic
        """
        import meshroom.decorators

        ast = AST(self.path / "setup.py")
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.setup_producer,
                order=order,
                topic=topic,
                mode=mode,
                title=title,
            )
        ast.save()
        return self

    def add_consumer_teardown_step(
        self,
        title: str,
        func: Callable | str,
        topic: str,
        mode: Mode = "push",
        order: str | None = None,
    ):
        """
        Append a generic teardown step to the product's setup.py
        to teardown a consumer for the given topic
        """
        import meshroom.decorators

        ast = AST(self.path / "setup.py")
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.teardown_consumer,
                order=order,
                topic=topic,
                mode=mode,
                title=title,
            )
        ast.save()
        return self

    def add_producer_teardown_step(
        self,
        title: str,
        func: Callable | str,
        topic: str,
        mode: Mode = "push",
        order: str | None = None,
    ):
        """
        Append a generic teardown step to the product's setup.py
        to teardown a producer for the given topic
        """
        import meshroom.decorators

        ast = AST(self.path / "setup.py")
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.teardown_producer,
                order=order,
                topic=topic,
                mode=mode,
                title=title,
            )
        ast.save()
        return self

    def list_pull_handlers(self):
        """
        List the pull handlers for this product, as found in its ./pull.py module
        pull handlers are all functions in the module whose name starts with "pull_"
        """
        return list_functions_from_module(
            self.path / "pull.py",
            startswith="pull_",
        )

    def list_capabilities(self, role: Role | None = None, topic: str | None = None, format: str | None = None):
        """
        List the Product's generic consumer/producer capabilities, either declared:
        - in definition.yaml's "consumes" and "produces" sections
        - via meshroom.decorators.setup_consumer(...) or meshroom.decorators.setup_producer(...) decorators in setup.py
        """
        from meshroom.decorators import SetupFunction

        out: set[Capability] = set()

        # Collect consumers from definition.yaml
        if role in ("consumer", None):
            for t, consumers in self.consumes.items():
                for consumer in consumers:
                    if (not topic or topic == t) and (not format or format == consumer.format or consumer.format is None):
                        out.add(Capability.consumer(t, consumer))

        # Collect producers from definition.yaml
        if role in ("producer", None):
            for t, producers in self.produces.items():
                for producer in producers:
                    if (not topic or topic == t) and (not format or format == producer.format or consumer.format is None):
                        out.add(Capability.producer(t, producer))

        # Collect capabilities declared in decorated setup functions
        self.import_python_modules()
        for sf in SetupFunction.get_all("setup"):
            if sf.product == self.name and sf.target_product is None:
                if (role is None or sf.role == role) and (topic is None or sf.topic == topic) and (format is None or sf.format == format or sf.format is None):
                    out.add(Capability(topic=sf.topic, role=sf.role, mode=sf.mode, format=sf.format))

        return list(out)

    def generate(self):
        print("Scaffold product", self.name)
        # TODO Generate the product boilerplate
        return self

    def pull(self):
        """
        Pull the product's SDK resources from its ./pull.py definitions
        pull handlers are all functions in the module whose name starts with "pull_"
        """
        (PROJECT_DIR / "mirrors" / self.name).mkdir(parents=True, exist_ok=True)
        if funcs := self.list_pull_handlers():
            for f in funcs:
                print(f"- Pull {self.name} via {f.__name__}")
                try:
                    f(path=PROJECT_DIR / "mirrors" / self.name)
                except Exception:
                    logging.error("Pull failed :", exc_info=True)
                print()
        else:
            return print("🚫 Nothing to do")

    def import_python_modules(self):
        """
        Import the product's python modules to collect all setup functions
        """
        for module in self.path.glob("*.py"):
            import_module(module)


class ProductSetting(Model):
    name: str
    type: Literal["string", "integer", "float", "boolean", "array", "object"] = "string"
    items: list["ProductSetting"] | Literal["string", "integer", "float", "boolean"] = []
    properties: list["ProductSetting"] = []
    default: str | int | float | bool | None = None
    description: str = ""
    secret: bool = False
    required: bool = False


class Integration(Model):
    """
    Implementation of an integration of :product to :target_product
    :product: The product on which the integration is deployed
    :target_product: The product to which the integration is connected
    :topic: The data topic exchanged between the two products
    :role: The role played by the product in the integration (consumer, producer, trigger, executor)
    :mode: The mode of the data exchange (producer push, or consumer pull)
    """

    product: str
    target_product: str
    topic: str
    role: Role
    mode: Mode = "push"
    format: str | None = None
    documentation_url: str = ""
    settings: dict[str, str] = {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path.with_suffix(".yml"), "w") as f:
            yaml.safe_dump(self.model_dump(), f)
        return self

    @staticmethod
    def load(filepath: Path):
        filepath = path_in_project(filepath)
        mode = "push"
        if filepath.stem.endswith("_pull"):
            topic, role, mode = filepath.stem.rsplit("_", maxsplit=2)
        else:
            topic, role = filepath.stem.rsplit("_", maxsplit=1)
        product = filepath.parent.parent.parent.name
        target_product = filepath.parent.name

        try:
            with open(filepath.with_suffix(".yml")) as f:
                config = yaml.safe_load(f)
        except Exception:
            config = {}

        return Integration.model_validate(
            {
                **config,
                "product": product,
                "target_product": target_product,
                "topic": topic,
                "role": role,
                "mode": mode,
            }
        )

    @property
    def plugs(self):
        if self.role in ("producer", "trigger"):
            return list(list_plugs(self.product, self.target_product, self.topic, self.mode))
        else:
            return list(list_plugs(self.target_product, self.product, self.topic, self.mode))

    @property
    def path(self):
        fn = f"{self.topic}_{self.role}"
        if self.format:
            fn += f"_{self.format}"
        if self.mode == "pull":
            fn += f"_{self.mode}"
        return path_in_project(PROJECT_DIR / "products" / self.product / "integrations" / self.target_product / fn)

    def matches(self, integration: "Integration"):
        """Check if this integration matches a complementary integration (e.g., consumer/producer)"""
        return (
            self.topic == integration.topic
            and (sorted((self.role, integration.role)) in (["consumer", "producer"], ["executor", "trigger"]))
            and (self.mode == integration.mode or self.mode is None or integration.mode is None)
            and (self.format == integration.format or self.format is None or integration.format is None)
        )

    def generate(self):
        print("Scaffold integration", self.product, "to", self.target_product, self.topic, self.role, self.mode)
        # TODO: Generate the integration code
        return self

    def add_setup_step(self, title: str, func: Callable | str, order: str | None = None):
        """
        Append a setup step to the integration's python code
        """
        import meshroom.decorators

        ast = AST(self.path.with_suffix(".py"))
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.setup,
                title=title,
                order=order,
                exclude_none=True,
            )
        ast.save()
        return self

    def add_teardown_step(self, title: str, func: Callable | str, order: str | None = None):
        """
        Append a teardown step to the integration's python code
        """
        import meshroom.decorators

        ast = AST(self.path.with_suffix(".py"))
        if f := ast.append_function(func):
            ast.add_imports(Integration, Plug)
            f.decorate(
                meshroom.decorators.teardown,
                title=title,
                order=order,
                exclude_none=True,
            )
        ast.save()
        return self

    def up(self, plug: "Plug"):
        """Setup the Integration on the source tenant"""
        print(f"Setup {self.role}")
        for i, f in enumerate(self.get_setup_functions("setup")):
            print(f"{i + 1}) {f.get_title()}")
            f.call(plug=plug, integration=self)
        print("✓ done")

    def down(self, plug: "Plug"):
        """Tear down the Integration from the source tenant"""
        print("Teardown", self.role)
        for i, f in enumerate(self.get_setup_functions("teardown")):
            print(f"{i + 1}) {f.get_title()}")
            f.call(plug=plug, integration=self)
        print("✓ done")

    def get_setup_functions(self, type: Literal["setup", "teardown"] | None = None):
        """
        List all the setup functions defined for this integration, declared either:
        - via meshroom.decorators.setup(...) decorator at integration-level
        - via meshroom.decorators.setup_consumer(...) or meshroom.decorators.setup_producer(...) decorators at product-level
        """
        from meshroom.decorators import SetupFunction
        from meshroom.generators import generate_setup_function

        # Sort the setup functions by their declared order
        funcs = sorted(sf for sf in SetupFunction.get_all(type) if sf.match(self))

        # If the integration overloads the setup hooks, keep only the overloaded ones and the ones marked to be kept
        if any(f.target_product for f in funcs):
            funcs = [f for f in funcs if f.target_product or f.keep_when_overloaded]

        # If no setup functions are found, try to generate a SetupFunction from the integration's and product's YAML specs
        if not funcs and (f := generate_setup_function(self)):
            funcs.append(f)

        return funcs


class Tenant(Model):
    """
    A Tenant is an instanciation of a product, configuring a set of Plug instances
    :name: The name of the tenant, which is also the directory name under /config/:product
    :product: The product the tenant instanciates
    """

    name: str
    product: str
    settings: dict = {}

    @staticmethod
    def load(path: Path):
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a plug directory")
        path = path_in_project(path)
        config = {}
        if (path / "config.yaml").is_file():
            with open(path / "config.yaml") as f:
                config = yaml.safe_load(f)
        config["name"] = path.name
        config["product"] = path.parent.name
        return Tenant.model_validate(config)

    def save(self):
        self.path.mkdir(parents=True, exist_ok=True)
        with open(self.path / "config.yaml", "w") as f:
            yaml.safe_dump(self.model_dump(), f)
        return self

    def get_settings_schema(self):
        return get_product(self.product).settings

    def set_secret(self, key: str, value: Any):
        """Store a secret value for this tenant (GPG encrypted)"""
        return secrets.set_secret(f"{self.product}_{self.name}_{key}", value)

    def get_secret(self, key: str, prompt_if_not_exist: str | bool | None = None):
        """Retrieve a secret value for this tenant (GPG encrypted)"""
        if prompt_if_not_exist is True:
            prompt_if_not_exist = f"Enter secret for {key}"

        return secrets.get_secret(f"{self.product}_{self.name}_{key}", prompt_if_not_exist=prompt_if_not_exist)

    @property
    def plugs(self):
        return list(list_plugs(src_tenant=self.name))

    @property
    def path(self):
        return path_in_project(PROJECT_DIR / "config" / self.product / self.name)


class Plug(Model):
    """
    A Plug is a configuration of an integration between two Tenants of two Products
    that defines the data exchange of a given topic

    :src_tenant: The source tenant of the integration, producing data
    :dst_tenant: The destination tenant of the integration, consuming data
    :topic: The data topic exchanged between the two tenants
    :mode: The mode of the data exchange (push or pull)

    A plug can be setup or torn down on the target systems via the up() and down() methods
    """

    src_tenant: str
    dst_tenant: str
    topic: str
    mode: Mode
    format: str | None = None
    src_config: dict = {}
    dst_config: dict = {}

    def __str__(self):
        out = f"{self.src_tenant} --[{self.topic}:{self.mode}]-> {self.dst_tenant}"
        if self.format:
            out += f" ({self.format})"
        return out

    @staticmethod
    def load(filepath: Path):
        filepath = path_in_project(filepath)
        config = {}
        with open(filepath) as f:
            config = yaml.safe_load(f)
        if "_" in filepath.stem:
            topic, mode = filepath.stem.rsplit("_", maxsplit=1)
        else:
            mode = "push"
            topic = filepath.stem
        config["topic"] = topic
        config["mode"] = mode
        config["src_tenant"] = filepath.parent.parent.parent.name
        config["dst_tenant"] = filepath.parent.name
        return Plug.model_validate(config)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            yaml.safe_dump(self.model_dump(), f)
        return self

    def delete(self):
        self.path.unlink()
        if not list(self.path.parent.iterdir()):
            self.path.parent.rmdir()
        if not list(self.path.parent.parent.iterdir()):
            self.path.parent.parent.rmdir()
        print(f"✓ Unplugged {self}")

    @property
    def path(self):
        fn = f"{self.topic}_{self.mode}" if self.mode == "pull" else self.topic
        return path_in_project(PROJECT_DIR / "config" / self.src_tenant / "plugs" / self.dst_tenant / f"{fn}.yaml")

    def get_secret(self, key: str, prompt_if_not_exist: str | bool | None = None):
        """Retrieve a secret value for this plug (GPG encrypted)"""
        if prompt_if_not_exist is True:
            prompt_if_not_exist = f"Enter secret for {key}: "

        return secrets.get_secret(
            f"{self.src_tenant}_{self.dst_tenant}_{self.topic}_{self.mode}_{key}",
            prompt_if_not_exist=prompt_if_not_exist or False,
        )

    def set_secret(self, key: str, value: Any):
        """Store a secret value for this plug (GPG encrypted)"""
        return secrets.set_secret(
            f"{self.src_tenant}_{self.dst_tenant}_{self.topic}_{self.mode}_{key}",
            value,
        )

    def get_consumer(self):
        """Get a suitable consumer to setup the consumer side of the integration"""
        consumers = list(list_integrations(self.dst_tenant, self.src_tenant, self.topic, role="consumer", mode=self.mode))
        if not consumers:
            raise ValueError(f"No consumer seems to be implemented for {self.src_tenant} -> {self.dst_tenant} {self.topic} in {self.mode} mode")
        elif len(consumers) > 1:
            raise ValueError(f"Multiple consumers found for {self.src_tenant} -> {self.dst_tenant} {self.topic} in {self.mode} mode")
        return consumers[0]

    def get_producer(self):
        """Get a suitable producer to setup the producer side of the integration"""
        producers = list(list_integrations(self.src_tenant, self.dst_tenant, self.topic, role="producer", mode=self.mode))
        if not producers:
            raise ValueError(f"No producer seems to be implemented for {self.src_tenant} -> {self.dst_tenant} {self.topic} in {self.mode} mode")
        elif len(producers) > 1:
            raise ValueError(f"Multiple producers found for {self.src_tenant} -> {self.dst_tenant} {self.topic} in {self.mode} mode")
        return producers[0]

    def get_src_tenant(self):
        """Get the source Tenant of the integration"""
        return get_tenant(self.src_tenant)

    def get_dst_tenant(self):
        """Get the destination Tenant of the integration"""
        return get_tenant(self.dst_tenant)

    def get_src_product(self):
        """Get the source Product of the integration"""
        return get_product(self.get_src_tenant().product)

    def get_dst_product(self):
        """Get the destination Product of the integration"""
        return get_product(self.get_dst_tenant().product)

    def up(self):
        """Setup the integration on the target Tenants"""
        print("Setup", self)

        # Look for a (consumer, producer) pair of integrations
        p = self.get_producer()
        c = self.get_consumer()

        p.up(self)
        c.up(self)
        return self

    def down(self):
        """Tear down the integration on the target Tenants"""
        print("Teardown", self)

        # Look for a (consumer, producer) pair of integrations
        p = self.get_producer()
        c = self.get_consumer()

        p.down(self)
        c.down(self)
        return self

    async def watch(self):
        """Watch the integration for data flowing through"""
        print("Watch", self.src_tenant, self.dst_tenant, self.topic, self.mode)
        # TODO Watch
        while True:
            await asyncio.sleep(1)
            print(".")

    def emulate(self):
        """Emulate data flowing through the integration"""
        print("Emulate", self.src_tenant, self.dst_tenant, self.topic, self.mode)
        # TODO Emulate
        return self


def set_project_dir(path: str | Path):
    """Set the base project directory where all meshroom data will be loaded and saved"""
    path = Path(path)
    global PROJECT_DIR
    PROJECT_DIR = path


def get_project_dir():
    return PROJECT_DIR


def path_in_project(path: str | Path):
    """Check if the given path is under the project directory"""
    if Path(path).resolve().is_relative_to(PROJECT_DIR.resolve()):
        return Path(path)
    raise ValueError(f"Path {path} is not under the project directory {PROJECT_DIR}")


def init_project(path: str | Path):
    """Initialize a new meshroom project in an empty or existing directory"""
    path = Path(path)
    set_project_dir(path)

    if path.is_dir() and list(PROJECT_DIR.iterdir()):
        if validate_meshroom_project(PROJECT_DIR):
            print("🚫 This meshroom project is already initialized")
            return False
        raise ValueError("Directory is not empty and is not a meshroom project")

    # Create the project directory structure
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_DIR / "products").mkdir(exist_ok=True)
    (PROJECT_DIR / "config").mkdir(exist_ok=True)

    print(f"✓ Meshroom project initialized at {PROJECT_DIR.absolute()}")
    return True


def validate_meshroom_project(path: str | Path):
    """Check if the given directory is a valid meshroom project"""
    path = Path(path)
    if not (path / "products").is_dir():
        return False
    return True


def list_products(tags: set[str] | None = None, search: str | None = None):
    """
    List all products found in the project's products/ directory
    If :tags is specified, only list products that have all the specified tags
    If :search is specified, only list products whose name match the search string
    """
    for product_dir in (PROJECT_DIR / "products").iterdir():
        if product_dir.is_dir() and (search is None or search in product_dir.name):
            p = get_product(product_dir.name)
            if tags is None or p.tags & tags:
                yield p


def list_tenants(product: str | None = None, search: str | None = None) -> Generator[Tenant, None, None]:
    """
    List all tenants found in the project's config/ directory
    If a product is specified, only list tenants for this product
    """
    path = PROJECT_DIR / "config"
    if product:
        path = path_in_project(path / product)
        if path.is_dir():
            for tenant_dir in path.iterdir():
                if tenant_dir.is_dir() and (search is None or search in tenant_dir.name):
                    yield Tenant.load(tenant_dir)
    else:
        if path.is_dir():
            for product_dir in path.iterdir():
                if product_dir.is_dir():
                    yield from list_tenants(product_dir.name, search=search)


def get_product(product: str):
    """Get a product by name"""
    path = path_in_project(PROJECT_DIR / "products" / product)
    if not path.is_dir():
        raise ValueError(f"Product {product} not found")

    return Product.load(path)


def get_tenant(tenant: str, product: str | None = None):
    """Get a tenant by name"""
    path = path_in_project(PROJECT_DIR / "config")
    if product:
        tenant_dir = path / product / tenant
        if tenant_dir.is_dir():
            return Tenant.load(tenant_dir)
    else:
        for t in list_tenants():
            if t.name == tenant:
                return t
    raise ValueError(f"Tenant {tenant} not found")


def create_tenant(product: str, name: str | None = None):
    name = name or product
    tenant_dir = path_in_project(PROJECT_DIR / "config" / product / name)
    if tenant_dir.exists():
        raise ValueError(f"🚫 Tenant {name} already exists")

    if not (PROJECT_DIR / "products" / product).is_dir():
        raise ValueError(f"Product {product} not found")

    tenant_dir.mkdir(parents=True, exist_ok=True)
    print(f"Create tenant {name} for product {product}")
    return Tenant.load(tenant_dir).save()


def delete_tenant(tenant: str, product: str | None = None):
    path = PROJECT_DIR / "config"
    get_tenant(tenant, product)
    if product:
        path = path_in_project(path / product / tenant)
        shutil.rmtree(path)
        print("✓ Removed", path)
    else:
        for product_dir in path.iterdir():
            if path_in_project(product_dir / tenant).is_dir():
                delete_tenant(tenant, product_dir.name)


def plug(src_tenant: str, dst_tenant: str, topic: str, mode: Mode | None = None, format: str | None = None):
    """
    Create a new Plug between two Tenants for a given topic
    """
    mode = mode or "push"

    # Ensure tenants exist
    src = get_tenant(src_tenant)
    dst = get_tenant(dst_tenant)

    try:
        # Check if the plug already exists (whatever the format)
        plug = get_plug(src_tenant, dst_tenant, topic, mode)
        print(f"🚫 Plug {plug}  already exists at {plug.path}")
        return plug
    except ValueError:
        producers = list(list_integrations(src.product, dst.product, topic, "producer", mode=mode or "push", format=format))
        consumers = list(list_integrations(dst.product, src.product, topic, "consumer", mode=mode or "push", format=format))
        triggers = list(list_integrations(src.product, dst.product, topic, "trigger", mode=mode or "push", format=format))
        executors = list(list_integrations(dst.product, src.product, topic, "executor", mode=mode or "push", format=format))
        for producer in producers:
            for consumer in consumers:
                if producer.matches(consumer):
                    plug = Plug(src_tenant=src_tenant, dst_tenant=dst_tenant, topic=topic, mode=mode, format=producer.format or consumer.format or format).save()
                    print(f"✓ Plugged {plug}")
                    return plug
        for trigger in triggers:
            for executor in executors:
                if trigger.matches(executor):
                    plug = Plug(src_tenant=src_tenant, dst_tenant=dst_tenant, topic=topic, mode=mode, format=trigger.format or executor.format or format).save()
                    print(f"✓ Plugged {plug}")
                    return plug

        raise ValueError(f"""❌ No integration between {dst_tenant} ({dst.product}) and {src_tenant} ({src.product}) for topic {topic} (mode={mode}) is implemented

    Consumers found: {consumers or 'None'}
    Producers found: {producers or 'None'}

    You may want to scaffold one via

    meshroom create integration {src.product} {dst.product} {topic} producer {f'--format {format} ' if format else ''}{f'--mode {mode} ' if mode not in (None, 'push') else ''}
    meshroom create integration {dst.product} {src.product} {topic} consumer {f'--format {format} ' if format else ''}{f'--mode {mode} ' if mode not in (None, 'push') else ''}
""")


def unplug(src_tenant: str, dst_tenant: str, topic: str, mode: Mode | None = None):
    try:
        get_plug(src_tenant, dst_tenant, topic, mode).delete()
    except ValueError:
        print(f"❌ Plug {src_tenant} --[{topic}:{mode}]-> {dst_tenant} not found")


def list_integrations(
    product: str | None = None,
    target_product: str | None = None,
    topic: str | None = None,
    role: Role | None = None,
    mode: Mode | None = None,
    format: str | None = None,
):
    path = PROJECT_DIR / "products"
    for product_dir in path.iterdir() if product is None else [path / product]:
        if not product_dir.is_dir():
            continue

        # 1) First look for specifically implemented integrations
        if (product_dir / "integrations").is_dir():
            for target_product_dir in (product_dir / "integrations").iterdir() if target_product is None else [product_dir / "integrations" / target_product]:
                if not target_product_dir.is_dir():
                    continue

                for integration_file in target_product_dir.iterdir():
                    if integration_file.is_file() and integration_file.suffix in (".yml", ".yaml"):
                        i = Integration.load(integration_file)
                        if (not topic or i.topic == topic) and (not role or i.role == role) and (not mode or i.mode == mode) and (not format or i.format == format):
                            yield i

        # 2) Look for matching pairs of generic product capabilities, with lower priority
        for a in get_product(product_dir.name).list_capabilities(role=role, topic=topic, format=format):
            for target_product_dir in path.iterdir() if target_product is None else [path / target_product]:
                if not target_product_dir.is_dir():
                    continue

                for b in get_product(target_product_dir.name).list_capabilities(topic=topic, format=format):
                    if a.matches(b):
                        # Yield generic Integration objects for matching capabilities
                        yield Integration(
                            product=product_dir.name,
                            target_product=target_product_dir.name,
                            topic=a.topic,
                            role=a.role,
                            mode=a.mode,
                            format=a.format or b.format,
                        )


def get_integration(product: str, target_product: str, topic: str, role: Role, mode: Mode | None = None):
    try:
        return list(list_integrations(product, target_product, topic, role, mode))[0]
    except Exception:
        return None


def list_plugs(
    src_tenant: str | None = None,
    dst_tenant: str | None = None,
    topic: str | None = None,
    mode: Mode | None = None,
):
    path = PROJECT_DIR / "config"
    if not path.is_dir():
        return
    for product_dir in path.iterdir():
        if (product_dir / "plugs").is_dir():
            for tenant_dir in (product_dir / "plugs").iterdir():
                if tenant_dir.is_dir():
                    for plug_file in tenant_dir.iterdir():
                        if plug_file.is_file():
                            p = Plug.load(plug_file)
                            if (
                                (not src_tenant or p.src_tenant == src_tenant)
                                and (not dst_tenant or p.dst_tenant == dst_tenant)
                                and (not topic or p.topic == topic)
                                and (mode is None or p.mode == mode)
                            ):
                                yield p


def get_plug(src_tenant: str, dst_tenant: str, topic: str, mode: Mode | None = None):
    for plug in list_plugs(src_tenant, dst_tenant, topic, mode):
        return plug
    raise ValueError(f"Plug {src_tenant} --[{topic}]-> {dst_tenant}  {mode or ''} not found")


def scaffold_integration(
    product: str,
    target_product: str,
    topic: str,
    role: Role = "producer",
    mode: Mode = "push",
    **kwargs,
):
    fn = f"{topic}_{role}" if mode in (None, "push") else f"{topic}_{role}_{mode}"
    path = path_in_project(PROJECT_DIR / "products" / product / "integrations" / target_product / fn)

    if path.with_suffix(".yml").is_file():
        print(f"🚫 Integration {product} -> {target_product} {topic} {role} {mode} already exists at {path}")
        return Integration.load(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    i = Integration.load(path).generate(**kwargs).save()

    print(f"✓ Integration {product} -> {target_product} {topic} {role} {mode} scaffolded at {path}")

    return i


def scaffold_product(name: str, **kwargs):
    path = path_in_project(PROJECT_DIR / "products" / name)
    if path.is_dir():
        print(f"🚫 Product {name} already exists, see {path}/definition.yaml")
        return Product.load(path)

    p = create_product(path, **kwargs).generate().save()
    print(f"✓ Product {name} scaffolded at {path}/definition.yaml")
    return p


def create_product(name: str, **kwargs):
    return Product.load(path_in_project(PROJECT_DIR / "products" / name)).update(**kwargs)


def up(src_tenant: str | None = None, dst_tenant: str | None = None, topic: str | None = None, mode: Mode | None = None):
    for plug in list_plugs(src_tenant, dst_tenant, topic, mode):
        plug.up()


def down(src_tenant: str | None = None, dst_tenant: str | None = None, topic: str | None = None, mode: Mode | None = None):
    for plug in list_plugs(src_tenant, dst_tenant, topic, mode):
        plug.down()


async def watch(src_tenant: str, dst_tenant: str, topic: str, role: Role, mode: Mode | None = None):
    return await get_plug(src_tenant, dst_tenant, topic, mode).watch(role)


def emulate(src_tenant: str, dst_tenant: str, topic: str, role: Role, mode: Mode = "push"):
    return get_plug(src_tenant, dst_tenant, topic, mode).emulate(role)
