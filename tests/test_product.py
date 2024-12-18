from meshroom.model import Capability, get_product, list_products, set_project_dir


def test_list_capabilities():
    set_project_dir("tests/fixtures/project1")
    assert set(get_product("myproduct").list_capabilities("consumer")) == {
        Capability(topic="events", role="consumer", mode="push", format="ecs"),
        Capability(topic="stuff", role="consumer", mode="pull"),
        Capability(topic="detection_rules", role="consumer", mode="push", format="sigma"),
    }
    assert set(get_product("myproduct").list_capabilities("producer")) == {
        Capability(topic="alerts", role="producer", mode="pull", format=None),
        Capability(topic="intelligence", role="producer", mode="pull", format="stix"),
    }

    assert {str(x) for x in get_product("myproduct").list_capabilities()} == {
        "alerts (pull)",
        "detection_rules (sigma)",
        "events (ecs)",
        "intelligence (pull stix)",
        "stuff (pull)",
    }


def test_list_products():
    set_project_dir("tests/fixtures/project1")
    assert {x.name for x in list_products()} == {"myproduct", "otherproduct"}


def test_match_capabilities():
    set_project_dir("tests/fixtures/project1")
    myproduct = get_product("myproduct")
    otherproduct = get_product("otherproduct")
    assert myproduct.list_capabilities("consumer", "stuff")[0].matches(Capability(topic="stuff", role="producer", mode="pull", format="anything"))
    assert myproduct.list_capabilities("consumer", "stuff")[0].matches(otherproduct.list_capabilities("producer", "stuff")[0])
