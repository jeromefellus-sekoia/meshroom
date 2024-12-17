from pathlib import Path
import shutil
import pytest

from meshroom.model import set_project_dir

PROJECT_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="session", autouse=True)
def setup_project():
    shutil.rmtree(PROJECT_DIR, ignore_errors=True)
    set_project_dir(PROJECT_DIR)
