import pytest
from meshroom.decorators import SetupFunction
from meshroom.model import Integration


def test_generic_setup_function():
    f = SetupFunction(
        product="myproduct",
        target_product=None,
        role="consumer",
        topic="stuff",
        func=lambda: ...,
        mode="pull",
        format=None,
        keep_when_overloaded=False,
        order=None,
        title="Make magic happen",
        type="setup",
    )

    assert f.match(Integration(product="myproduct", target_product="otherproduct", role="consumer", topic="stuff", mode="pull", format="ecs"))
    assert f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull"))
    assert f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))

    assert not f.match(Integration(product="otherproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="producer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="push", format="whatever"))


def test_specifig_setup_function():
    f = SetupFunction(
        product="myproduct",
        target_product="otherproduct",
        role="consumer",
        topic="stuff",
        func=lambda: ...,
        mode="pull",
        format=None,
        keep_when_overloaded=False,
        order=None,
        title="Make magic happen",
        type="setup",
    )

    assert f.match(Integration(product="myproduct", target_product="otherproduct", role="consumer", topic="stuff", mode="pull", format="ecs"))
    assert f.match(Integration(product="myproduct", target_product="otherproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))

    assert not f.match(Integration(product="otherproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="producer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="push", format="whatever"))


def test_specifig_setup_function_with_format():
    f = SetupFunction(
        product="myproduct",
        target_product="otherproduct",
        role="consumer",
        topic="stuff",
        func=lambda: ...,
        mode="pull",
        format="ecs",
        keep_when_overloaded=False,
        order=None,
        title="Make magic happen",
        type="setup",
    )

    assert f.match(Integration(product="myproduct", target_product="otherproduct", role="consumer", topic="stuff", mode="pull", format="ecs"))
    assert not f.match(Integration(product="myproduct", target_product="otherproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))

    assert not f.match(Integration(product="otherproduct", target_product="myproduct", role="consumer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="producer", topic="stuff", mode="pull", format="whatever"))
    assert not f.match(Integration(product="myproduct", target_product="myproduct", role="consumer", topic="stuff", mode="push", format="whatever"))
