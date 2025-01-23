#!/bin/bash
# E2E Test to validate the docs/tutorial.md works as expected

cd $(dirname $0)/../..
rm -rf tests/e2e/data


### 0. Setup a meshroom project

# A meshroom project is a git-backed directory on your computer. Let's setup one via

meshroom init tests/e2e/data
cd tests/e2e/data

# We can list list our Products and Instances using
meshroom list products
meshroom list instances
# which confirms we have no products and no instances yet.

### 1. Gather knowledge about existing products

# Imagine we want to incorporate a Sekoia.io SOC platform tenant into our mesh. We can leverage existing definitions from [https://github.com/jeromefellus-sekoia/meshroom/tree/master/example/products/sekoia](https://github.com/jeromefellus-sekoia/meshroom/tree/master/example/products/sekoia), by simply copying the subdirectory to our project's `products/` folder:
mkdir -p tmp
curl -L -o tmp.tar.gz https://github.com/jeromefellus-sekoia/meshroom/tarball/master
tar -xzf tmp.tar.gz -C tmp
mv tmp/*/example/products/sekoia products/sekoia
rm -rf tmp tmp.tar.gz

# Happily, the sekoia product contains `@pull` hooks, allowing us to gather from Sekoia's official catalog the whole set of integrations available between Sekoia.io and 3rd-party products (here, so-called intake formats and playbook actions). Calling
meshroom pull sekoia

# yields dozen of new products along with their own capabilities to the extent of what Sekoia.io can interop with. You'd probably need to gather and pull more product knowledge to enrich those 3rd-party product definitions and reach a sufficiently large and accurate capabilities graph to start instantiating a mesh from it.
meshroom list products

### 2. Integrate your product

rm -rf products/myedr

# This tutorial assumes we're a vendor of a new product that didn't get a meshroom definition yet. So let's create it from scratch, or better, using one of the provided product capabilities templates, found under [https://github.com/jeromefellus-sekoia/meshroom/tree/master/meshroom/templates/products](https://github.com/jeromefellus-sekoia/meshroom/tree/master/meshroom/templates/products)
meshroom create product myedr --from edr

cat >> products/myedr/definition.yaml <<EOF
consumes:
   threats:
      - format: stix
        mode: push
produces:
   threats:
      - format: stix
        mode: pull
   events:
      - format: json
        mode: push
executes:
   search_threat:
      - {}
EOF

# Create the `products/myedr/search_threat.py file containing
cat >> products/myedr/search_threat.py <<EOF
from meshroom.decorators import setup_executor
from meshroom.model import Integration, Plug, Instance

@setup_executor("search_threat")
def setup_threat_search_api_via_myedr_plugin(integration: Integration, plug: Plug, instance: Instance):
    some_value = instance.settings.get("some_setting")
    some_secret = plug.get_secret("SOME_SECRET")
    api_key = instance.get_secret("API_KEY")
    raise NotImplementedError("Implement the setup mechanism here")
EOF


# Let's add those required secrets and settings to our product's `definition.yaml`
cat >> products/myedr/definition.yaml <<EOF
settings:
  - name: API_KEY
    secret: true
  - name: some_setting
    default: whatever
EOF

# Let's create a suitable Integration for that:
meshroom create integration myedr sekoia search_threat executor

# We can confirm the existence of our new product and integrations via
meshroom list products mye
meshroom list integrations myedr

### 3. Create a mesh

pass MESHROOM_SEKOIA_API_KEY | meshroom add sekoia mysekoia -s API_KEY
echo "plop" | meshroom add myedr -s API_KEY

# Now, let's **plug** both products, so that mysekoia can consume myedr's events and myedr can execute mysekoia's queries for threat searches.

meshroom plug events myedr mysekoia
meshroom plug search_threat mysekoia myedr

# Oh no ! Meshroom CLI tells us that it can't find an integration for the trigger side of the second plug. Indeed, we've defined how to setup a myedr plugin to execute threat searches, but no Sekoia.io integration to actually trigger it from Sekoia.
# Let's fix that
meshroom create integration sekoia myedr search_threat trigger --mode=push

# and confirm it worked
meshroom list integrations sekoia myedr

# Make our sekoia->myedr integration be fully owned by sekoia (owns_both=True)
sed -i 's/owns_both=False/owns_both=True/' products/sekoia/integrations/myedr/search_threat_trigger.py

# Contrarily to the previous call to `meshroom create integration`, this has created many files under the `products/sekoia/integrations/myedr/` folder, where we may recognize an almost complete Sekoia.io custom playbook action as one can find examples at [https://github.com/SEKOIA-IO/automation-library](https://github.com/SEKOIA-IO/automation-library). This integration has been automatically scaffolded because Sekoia.io's vendor has defined a `@scaffold` hook for this kind of trigger. This hook generated all the boilerplate code required to build a custom playbook action that will trigger executions on 3rd-party APIs. All we need to do is to actually implement the TODOs left in the boilerplate. We won't cover this specific business here, but once you've coded your own logic, you can call again
meshroom plug search_threat mysekoia myedr

# should then show 2 instances and 1 plug connecting them.
meshroom list instances
meshroom list plugs

# Let's commit our work to some git repository
git add .
git commit -a -m "Initial commit"
git remote add origin git@github.com:jeromefellus-sekoia/test-meshroom-custom-integration1.git
git branch
git push -f -u origin master

### 4. Meshroom up 🎉 !

# Once you get a valid and satisfactory mesh of Instances and Plugs, you're ready to call
meshroom up

# To check everything works as expected, we can use two handy commands :
meshroom produce events myedr mysekoia
meshroom watch events myedr mysekoia

### 5. Meshroom down

meshroom down

### 6. Meshroom publish

meshroom publish sekoia myedr search_threats

# By the way, you can also play the trigger from command line via
meshroom trigger search_threats mysekoia myedr
