release:
	@VERSION=$$(poetry version -s); git tag -a v$${VERSION} -m "meshroom v$${VERSION}"; git push origin v$${VERSION}; \
	gh release create "v$${VERSION}" --title "meshroom v$${VERSION}" --generate-notes

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
