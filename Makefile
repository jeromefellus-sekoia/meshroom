VERSION=$(shell poetry version --short)

build:
	docker build -t meshroom:$(VERSION) .