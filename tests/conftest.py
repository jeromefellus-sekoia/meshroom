import os
from pathlib import Path
import shutil
from unittest.mock import patch
import pytest

patch("getpass.getpass", return_value="password")
patch("getpass.unix_getpass", return_value="password")


PROJECT_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="function", autouse=True)
def setup_project():
    from meshroom.model import set_project_dir

    shutil.rmtree(PROJECT_DIR, ignore_errors=True)
    set_project_dir(PROJECT_DIR)


def skip_during_ci(func):
    """Decorator to skip a test if running in Github CI."""
    if os.getenv("GITHUB_RUN_ID"):
        return pytest.mark.skip(reason="Skipped during CI, please run interactively")(func)
    return func
