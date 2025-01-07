import pytest
from meshroom.model import Plug, get_plug, list_plugs, plug, set_project_dir, unplug


def test_plug():
    return
    set_project_dir("tests/fixtures/project1")
    p = plug("otherproduct", "myproduct", "stuff", "pull", "json")

    assert p == Plug(
        src_instance="otherproduct",
        dst_instance="myproduct",
        topic="stuff",
        mode="pull",
        format="json",
    )

    assert get_plug("otherproduct", "myproduct", "stuff", "pull") == p

    assert list(list_plugs()) == [p]
    assert list(list_plugs("otherproduct", "myproduct")) == [p]
    assert list(list_plugs(topic="stuff")) == [p]

    plug("otherproduct", "myproduct", "stuff", "pull", "json")
    assert list(list_plugs()) == [p]

    unplug("otherproduct", "myproduct", "stuff", "pull")

    with pytest.raises(ValueError):
        get_plug("otherproduct", "myproduct", "stuff", "pull")
