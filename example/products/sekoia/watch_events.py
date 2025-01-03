from meshroom.decorators import watch
from .api import SekoiaAPI
from meshroom.model import Plug, Tenant


@watch("events")
def watch_events(tenant: Tenant, plug: Plug | None = None):
    """Watch events received by a Sekoia intake (when plug is provided) or by a whole Sekoia.io community otherwise."""
    api = SekoiaAPI(
        tenant.settings.get("region", "fra1"),
        tenant.get_secret("API_KEY"),
    )

    yield from api.watch_events(plug.settings["intake_uuid"] if plug else None)
