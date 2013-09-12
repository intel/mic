PYTHON ?= python
VERSION = $(shell sed -ne 's/__version__\s*=\s*"\(.*\)"/\1/p ' mic/__init__.py)
TAGVER = $(shell git describe --abbrev=0 --tags)

PKGNAME = mic

all: build

build:
	$(PYTHON) setup.py build

_archive: man
	git archive --format=tar --prefix=$(PKGNAME)-$(VER)/ $(TAG) | tar xpf -
	git show $(TAG) --oneline | head -1 > $(PKGNAME)-$(VER)/commit-id
	rm -rf $(PKGNAME)-$(VER)/tests
	tar zcpf $(PKGNAME)_$(VER).tar.gz $(PKGNAME)-$(VER)
	rm -rf $(PKGNAME)-$(VER)

dist: VER=$(VERSION)
dist: TAG='HEAD'
dist: _archive

release: VER=$(TAGVER)
release: TAG=$(TAGVER)
release: _archive

man:
	rst2man doc/man.rst > doc/mic.1

install: build
	$(PYTHON) setup.py install

develop: build
	$(PYTHON) setup.py develop

test:
	cd tests/ && $(PYTHON) suite.py

clean:
	rm -f *.tar.gz
	rm -f doc/mic.1
	rm -rf *.egg-info
	rm -rf build/ dist/
