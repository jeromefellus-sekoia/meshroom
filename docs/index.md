# Meshroom

A command-line tool to build and manage Cybersecurity Mesh Architectures (CSMA).

## Philosophy
As defined by Gartner, a [Cybersecurity Mesh Architecture](https://www.gartner.com/en/information-technology/glossary/cybersecurity-mesh) is a set of interoperated cybersecurity services, each fulfilling a specific functional need (SIEM, EDR, EASM, XDR, TIP, *etc*).
Adopting the CSMA and Meshroom's philosophy means choosing an interconnected ecosystem of high-quality products with specialized scopes rather than a captive all-in-one solution.
Therefore, it also means :
* Adopting standard formats and protocols to share data and informations between products (STIX, ECS, OCSF, OpenC2, syslog, CEF, *etc*) rather than proprietary ones
* Leveraging Open APIs to make your products communicate with eachother
* Exploiting products' extensibility via plugins and open-source components to strengthen the interoperability with other products

## Who ?

### As a vendor : fight the N-to-N integration curse

Cybersecurity vendors know it well : integrating with other cybersecurity products consumes time and human resources. Integration teams feel so sad that every vendor has to spend those resources to develop an integration with every other vendor : this is the N-to-N integration curse. This curse mostly originates from:
* Poor adoption of standard formats, protocols and API layouts to interoperate cybersecurity solutions
* Lack of open resources and documentation to start communicating and controling a given product
* Small actors are overwhelmed by the numerous integration opportunities with major actors, but won't factorise their contribution to make one integration suit all 3rd-party products
* Every actor must keep hundreds of vendor-specific integrations up to date according to hundreds of non-coordinated roadmaps and breaking changes

Meshroom helps cybersecurity vendors build integration between their products and other solutions, while keeping the integration burden as low a possible.
To do so, `meshroom` comes with a set of predefined product templates categorized according to Gartner's [Hype Cycle for Security Operations, 2024](https://www.gartner.com/interactive/hc/5622491?ref=solrAll&refval=433161127). By publishing your product's functional surface from one of this template, you encourage the adoption of standard API layouts, formats and protocols, eventually converging from a N-to-N integration burden to an ideal N product definitions repository, where every new vendor can costlessly plug with the N previously declared products.

### As a MSSP : setup a full cybersecurity mesh via declarative and versionable manifests

Setting up a SOC is also a time-consuming operation. Sadly, MSSPs in charge of many similar information systems will often repeat those very same time-consuming steps again and again, switching from one solution's configuration interface to another one's console. Eventually, this will involve wildly manipulating API keys and administration forms, resulting in errors, security holes and blind spots. Many MSSPs maintain a run book of manual setup steps, and most of them automate part of those steps to get a SOC up-and-running within, say, days or perhaps hours...

Meshroom helps DevSec operators to setup a full meshed SOC made of dozens of tenants in a single CLI command : `meshroom up`.
Because Meshroom projects are versioned, you can push and share SOC architectures via GitHub or your favorite forge, while keeping trace of every setup and provisioning processes executed.

When your SOC grows to dozens of interoperated products, it becomes hard to visualize where data and controls flow between them. Meshroom provides an easy to use graph model documenting:
* all capabilities exposed by the products you are using
* all available integrations they offer to other products
* all the active connections (know as `Plugs` within Meshroom) between products (aka `producer`/`consumer` and `trigger`/`executor` relationships)

### As a developer : painless developer experience to build and publish custom product additions

Many cybersecurity platforms offer extensibility capabilities via plugins, custom formats, custom rules, custom actions, *etc*. Here again, there's no accepted standard and every vendor defines its own approach (YAML files, python code, no-code workflows, *etc*). Yet, products interoperability often rely on contributing custom additions to one or both ends. Of course, this scope is often the worst documented part, and developers are left with trial-and-error quasi-reverse ninja approaches to understand how to make product A with product B communicate. In the end, you'll eventually succeed in getting a working plugin, but then face the un-coordinated maze of extension homologation processes each vendor mandates to make your contribution public.

Meshroom helps cybersecurity vendors to expose a single standard contribution model for:
* setting up custom software additions when interoperability mandates so
* compiling everything into a product plugin suitable for publication
* publishing as a PR to GitHub or other marketplaces
