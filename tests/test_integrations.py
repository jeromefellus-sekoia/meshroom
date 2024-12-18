from meshroom.model import Integration, list_integrations, set_project_dir


def test_list_integrations():
    set_project_dir("tests/fixtures/project1")
    assert list(list_integrations()) == [
        Integration(product="myproduct", target_product="otherproduct", topic="stuff", role="consumer", mode="pull", format="json", documentation_url="", settings={}),
        Integration(product="otherproduct", target_product="myproduct", topic="stuff", role="producer", mode="pull", format="json", documentation_url="", settings={}),
    ]
