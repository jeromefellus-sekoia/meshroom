# Concepts

## Integration lifecycle

TODO CYCLE SCHEMA

## Capabilities graph

Formally, a cybersecurity mesh architecture (CSMA) is a directed graph of products talking to eachother.
More precisely, it is an overlay of 2 graphs:

* The **capabilities graph**, which expresses the set of all products that can be interoperated with eachother and what functional capacity they expose. Nodes of this graph are Product capabilities, and edges connect complementary capabilities. For example, one product may **consume** alerts **produced** by another product, or can **execute** actions **triggered** by another one. Edges thus characterise interop opportunities about a certain **Topic** between a source product and a destination product. The direction of the edges materializes the dataflow : the source product **produces/triggers** information (resp. actions) that the destination product **consumes/executes**. An edge exists as soon as the products define a compatible producer (or trigger) / consumer (resp. executor) pair of **Integrations**. The edge also carries the **roles** in the data exchange

    * in **push** mode, the producer is **active** and the consumer is **passive** (*e.g.* a Syslog forwarder)
    * in **pull** mode, the producer is **passive** and the consumer is **active** (*e.g.* an HTTP GET API)

Therefore, an edge exist between product couples that expose complementary integrations for compatible topics, and match formats or other compatibility criteria you may need to refine the scope of a capability.

The density if the capabilities graph measures the "openness" of the products constellation ; one wants to maximize the number of allowed interops between cybersecurity solutions available on the market

* The **Mesh** graph itself, which is an instanciation of several product **Instances** connected to eachother by **Plugs** who leverage compatible Integrations over the underlying capabilities graph. Instances correspond to actual user tenants of the underlying products, and plugs are live connections between those tenants. In order to setup the defined plugs, instances must be configured to enable the corresponding production/consumption triggering/execution logic, potentially via custom additions to the products themselves. Meshroom's spirit is to make all this configuration and provisioning as simple as a single `meshroom up` command.

To do so, Products, Integrations, Instances and Plugs are defined via YAML manifests and vendor code additions when required. All these files belong to a **git-backed repository** that can be shared, versioned via git and manipulated via the Meshroom CLI, exactly as, say, Helm charts can be shared among a community of Kubernetes users.

Some **sensitive data**, like API keys and other secrets used to teleoperate the Instances are natively held and managed by Meshroom in a **local GPG secrets store**, that can also be shared following a classical GPG assymetric cryptography process. This decreases the risk of leak resulting from a spread of secrets used to co-ordinate numerous tenants, while easing the **sharing** of a full read-to-use SOC configuration.


## Product

`meshroom create product`

`meshroom list products`

## Integration

`meshroom create integration`

`meshroom list integrations`

## Instance

`meshroom add`

`meshroom list instances`

`meshroom configure`

secrets GPG

## Plug

`meshroom plug`

`meshroom unplug`

`meshroom list plugs`

## Up/down

`meshroom up`
`meshroom down`


## Hooks

* setup
* teardown
* scaffold
* pull
* publish
* produce
* watch

## Meshroom project structure

A Meshroom project is a git-backed directory on your computer, that you can version and share via your favorite online git service. The local project itself has the following structure:

````
┃
┣━ products                      🮤━━━  All products available in the capabilities graph
┃  ┗━ product_a
┃     ┣━ definition.yaml              🮤━━━  Define capabilities of product_a
┃     ┣━ setup.py                     🮤━━━  Various python files with generic hooks for product_a's integrations
┃     ┗━ integrations                 🮤━━━  All integration offered by product_a
┃        ┗━ product_b                 🮤━━━  All integration offered by product_a with product_b
┃           ┣━ events_consumer.yaml       🮤━━━  An integration product_a -[events]-> product_b in push mode
┃           ┣━ events_consumer.py         🮤━━━  Hooks for the above integration
┃           ┣━ events_consumer_pull.yaml  🮤━━━  An integration product_a -[events]-> product_b in pull mode
┃           ┗━ events_consumer_pull.py    🮤━━━  Hooks for this latter integration
┃  ┗━ product_b
┃     ┗━ ...                     🮤━━━ same structure for each product...
┃
┣━ instances                   🮤━━━  Define the instances used in this project's mesh
┃  ┗━ product_a                   🮤━━━  Instances for product_a
┃     ┗━ instance_a               🮤━━━  Some product_a's instance, here called "instance_a"
┃        ┣━ config.yaml             🮤━━━  Non-sensitive configuration for instance_a
┃        ┗━ plugs                   🮤━━━  Plugs whose source is instance_a
┃           ┗━ instance_b                🮤━━━  Plugs whose destination is instance_b
┃              ┗━ event_consumer_pull.yaml   🮤━━━  Config for plug instance_a -[events]-> instance_b in pull mode
┃  ┗━ product_b
┃     ┗━ instance_product_b
┃        ┗━ ...
┣━ secrets.gpg      🮤━━━  GPG-encrypted store of all instances' secrets
````

This is a minimal example, your project may contain additional files, such as .gitignore, README.md and other documentation or scripts for automating stuff.
