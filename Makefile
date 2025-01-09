release:
	git add pyproject.toml
	git commit -m "Release v$$(poetry version -s)"
	git push origin master
	@VERSION=$$(poetry version -s); git tag -a v$${VERSION} -m "meshroom v$${VERSION}"; git push origin v$${VERSION}; \

major:
	git checkout master
	poetry version major
	$(MAKE) release

minor:
	git checkout master
	poetry version minor
	$(MAKE) release

patch:
	git checkout master
	poetry version patch
	$(MAKE) release
