#
# Common Makefile for building RPMs
#

NAME := xen
SPECFILE := xen.spec

WORKDIR := $(shell pwd)
SPECDIR ?= $(WORKDIR)
SRCRPMDIR ?= $(WORKDIR)/srpm
BUILDDIR ?= $(WORKDIR)
RPMDIR ?= $(WORKDIR)/rpm
SOURCEDIR := $(WORKDIR)
VERSION := $(shell cat version)

NO_OF_CPUS := $(shell grep -c ^processor /proc/cpuinfo)

RPM_DEFINES := --define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SPECDIR)" \
		--define "_builddir $(BUILDDIR)" \
		--define "_srcrpmdir $(SRCRPMDIR)" \
		--define "_rpmdir $(RPMDIR)" \
		--define "version $(VERSION)" \
		--define "jobs $(NO_OF_CPUS)"

VER_REL := $(shell rpm $(RPM_DEFINES) -q --qf "%{VERSION} %{RELEASE}\n" --specfile $(SPECFILE)| head -1)

ifndef NAME
$(error "You can not run this Makefile without having NAME defined")
endif
ifndef VERSION
$(error "You can not run this Makefile without having VERSION defined")
endif
ifndef RELEASE
RELEASE := $(word 2, $(VER_REL))
endif

all: help

SRC_BASEURL := http://bits.xensource.com/oss-xen/release/${VERSION}/
SRC_FILE := xen-${VERSION}.tar.gz
SIGN_FILE := xen-${VERSION}.tar.gz.sig

URL := $(SRC_BASEURL)/$(SRC_FILE)
URL_SIGN := $(SRC_BASEURL)/$(SIGN_FILE)

get-sources: $(SRC_FILE) $(SIGN_FILE)

$(SRC_FILE):
	@echo -n "Downloading $(URL)... "
	@wget -q $(URL)
	@echo "OK."

$(SIGN_FILE):
	@echo -n "Downloading $(URL_SIGN)... "
	@wget -q $(URL_SIGN)
	@echo "OK."


verify-sources:
	@gpg --verify $(SIGN_FILE) $(SRC_FILE)

.PHONY: clean-sources
clean-sources:
ifneq ($(SRC_FILE), None)
	-rm $(SRC_FILE)
endif


#RPM := rpmbuild --buildroot=/dev/shm/buildroot/
RPM := rpmbuild 

RPM_WITH_DIRS = $(RPM) $(RPM_DEFINES)

rpms: get-sources $(SPECFILE)
	$(RPM_WITH_DIRS) -bb $(SPECFILE)
	rpm --addsign $(RPMDIR)/x86_64/*$(VERSION)-$(RELEASE)*.rpm

rpms-nobuild:
	$(RPM_WITH_DIRS) --nobuild -bb $(SPECFILE)

rpms-just-build: 
	$(RPM_WITH_DIRS) --short-circuit -bc $(SPECFILE)

rpms-install: 
	$(RPM_WITH_DIRS) -bi $(SPECFILE)

prep: get-sources $(SPECFILE)
	$(RPM_WITH_DIRS) -bp $(SPECFILE)

srpm: get-sources $(SPECFILE)
	$(RPM_WITH_DIRS) -bs $(SPECFILE)

verrel:
	@echo $(NAME)-$(VERSION)-$(RELEASE)

# mop up, printing out exactly what was mopped.

.PHONY : clean
clean ::
	@echo "Running the %clean script of the rpmbuild..."
	$(RPM_WITH_DIRS) --clean --nodeps $(SPECFILE)

update-repo-current:
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE)*.rpm ../yum/current-release/current/dom0/rpm/

update-repo-unstable:
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE)*.rpm ../yum/current-release/unstable/dom0/rpm/

update-repo-installer:
	ln -f rpm/x86_64/xen-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-debuginfo-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-doc-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-hypervisor-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-runtime-$(VERSION)-$(RELEASE)*.rpm ../installer/yum/qubes-dom0/rpm/
	cd ../installer/yum && ./update_repo.sh

help:
	@echo "Usage: make <target>"
	@echo
	@echo "get-sources      Download kernel sources from kernel.org"
	@echo "verify-sources"
	@echo
	@echo "prep             Just do the prep"	
	@echo "rpms             Build rpms"
	@echo "rpms-nobuild     Skip the build stage (for testing)"
	@echo "rpms-just-build  Skip packaging (just test compilation)"
	@echo "srpm             Create an srpm"
	@echo
	@echo "make update-repo-current  -- copy newly generated rpms to qubes yum repo"
	@echo "make update-repo-unstable -- same, but to -testing repo"
