# Contributing to Meshroom

Meshroom is reputed to work on python>=3.10.
CI matrix tests upon commit push are in place to ensure contributions won't break that compatibility.

### Pull Requests

We welcome pull requests! If you're planning to contribute code, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Test your changes thoroughly.
5. Commit your changes (`git commit -m 'Add some feature'`).
6. Push to the branch (`git push origin feature/YourFeature`).
7. Open a pull request.
8. Your PR should pass CI test to be mergeable
9. Pull requests need at least one approval to get merged

### Style Guide

We strongly encourage (but don't mandate) the use of [ruff](https://docs.astral.sh/ruff/) linter

### Maintainers

Don't hesitate to reach out to [OXA project's](https://github.com/opencybersecurityalliance/oxa) contributors to become a maintainer.
Maintainers can trigger releases from the master branch using the provided [Makefile](Makefile) targets:

```bash
make patch # to release a new semver patch-level release
make minor # to release a new semver minor-level release
make major # to release a new semver major-level release
```

Release notes are automatically generated from merged PRs via github actions, as well as publishing to [pypi.org](pypi.org)