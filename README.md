# Meshroom, the Cybersecurity Mesh Assistant

A command-line tool to build and manage Cybersecurity Mesh Architectures (CSMA), initiated by the OXA project.

I'm python-based, install me via pip using

```bash
pip install meshroom
```

### What is CSMA ?

A Cybersecurity Mesh Architecture is a graph of interoperated cybersecurity services, each fulfilling a specific functional need (SIEM, EDR, EASM, XDR, TIP, *etc*). Adopting Meshroom's philosophy means promoting an interconnected ecosystem of high-quality products with specialized scopes rather than a captive all-in-one solution.

### Where to start ?

Run

```bash
meshroom --help
```

or browse the documentation to start building meshes.

### Autocompletion

On Linux, you can enable meshroom's autocompletion in your terminal by running

```bash
eval "$(_MESHROOM_COMPLETE=bash_source meshroom)"
```

or adding it to your `.bashrc`