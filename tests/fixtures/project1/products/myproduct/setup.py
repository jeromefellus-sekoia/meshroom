from meshroom.decorators import setup_consumer


@setup_consumer("events", format="ecs")
def setup_consumer_for_events():
    pass


@setup_consumer("stuff", mode="pull")
def setup_pull_consumer_for_stuff():
    pass
