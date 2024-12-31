import shutil
from uuid import uuid4
from meshroom.model import Integration, Tenant
from meshroom.decorators import scaffold_trigger
from .api import SekoiaAPI


@scaffold_trigger("action")
def scaffold_custom_action_trigger(integration: Integration):
    """Scaffold a new action trigger backed by a custom Sekoia.io automation action"""

    # NOTE: We can't leverage the sekoia automation SDK here since it is Pydantic-v1 based, which conflicts with Meshroom's Pydantic-v2
    #       so let's scaffold module files by ourself from static templates in examples/

    name = integration.target_product
    path = integration.path.parent / "dist" / "automations" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    uuid = str(uuid4())

    # Scaffold setup steps if needed
    python_file = integration.path.with_suffix(".py")
    if not python_file.is_file() or not python_file.read_text():
        # Add required import statements
        python_file.write_text("""
from ...api import SekoiaAPI
import yaml
import json
""")
        integration.add_setup_step("Push action to git repo", git_push_automation_module, order=0)
        integration.add_setup_step("Sync action from git repo", update_playbook_module_from_git, order=1)

    # Scaffold files from examples/action_trigger when they don't exist
    example_path = integration.get_product().path / "examples/action_trigger"

    for fn in example_path.rglob("*.*"):
        dst_file = path / fn.relative_to(example_path)
        if fn.is_file() and (not dst_file.is_file() or dst_file.read_text() == ""):
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            print("    Generate", dst_file)
            if fn.suffix == ".png":
                shutil.copy(fn, dst_file)
            else:
                dst_file.write_text(
                    # Replace placeholders
                    fn.read_text().replace("{{UUID}}", uuid).replace("{{NAME}}", name)
                )

    integration.save()


def git_push_automation_module(integration: Integration):
    """A setup hook that pushes the automation module to a git repo"""
    from meshroom.git import git_push

    name = integration.target_product
    path = integration.path.parent / "dist" / "automations" / name
    if git_push(True, path, f"Update {name} automation module"):
        print(f"Automation module {name} successfully pushed to git repo")
    else:
        print(f"Automation module {name} is up-to-date in git repo")


def update_playbook_module_from_git(integration: Integration, tenant: Tenant):
    """A setup hook that syncs an integration's automation module from the git repo"""
    from meshroom.git import git_get_remote, git_get_branch
    from meshroom.model import get_project_dir
    from uuid import uuid4
    import re

    name = integration.target_product
    path = integration.path.parent / "dist" / "automations" / name
    api = SekoiaAPI(
        tenant.settings.get("region", "fra1"),
        tenant.get_secret("API_KEY"),
    )

    # Ensure the git URL is in HTTPS scheme
    https_url = re.sub(r"^git@(.+):(.+?)/(.+?)(?:\.git)?$", r"https://\1/\2/\3", git_get_remote())

    # Trigger a pull of the automation module's code from the git repo
    api.pull_custom_integration(https_url, git_get_branch(), path.relative_to(get_project_dir()).as_posix(), str(uuid4()))
