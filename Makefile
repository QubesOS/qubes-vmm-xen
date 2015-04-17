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
RELEASE := $(shell cat rel)

DIST_DOM0 ?= fc13

DISTFILES_MIRROR := http://sourceforge.net/projects/qubesos/files/distfiles/
NO_OF_CPUS := $(shell grep -c ^processor /proc/cpuinfo)

RPM_DEFINES := --define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SPECDIR)" \
		--define "_builddir $(BUILDDIR)" \
		--define "_srcrpmdir $(SRCRPMDIR)" \
		--define "_rpmdir $(RPMDIR)" \
		--define "version $(VERSION)" \
		--define "jobs $(NO_OF_CPUS)"

ifndef NAME
$(error "You can not run this Makefile without having NAME defined")
endif
ifndef VERSION
$(error "You can not run this Makefile without having VERSION defined")
endif
ifndef RELEASE
$(error "You can not run this Makefile without having RELEASE defined")
endif

all: help

SRC_BASEURL := http://bits.xensource.com/oss-xen/release/${VERSION}/
SRC_FILE := xen-${VERSION}.tar.gz
SIGN_FILE := xen-${VERSION}.tar.gz.sig

GRUB_FILE := grub-0.97.tar.gz
GRUB_URL := ftp://alpha.gnu.org/gnu/grub/$(GRUB_FILE)
GRUB_SIGN_SUFF := .sig

LWIP_FILE := lwip-1.3.0.tar.gz
LWIP_URL := http://download.savannah.gnu.org/releases/lwip/older_versions/$(LWIP_FILE)
LWIP_SIGN_SUFF := .sig

NEWLIB_FILE := newlib-1.16.0.tar.gz
NEWLIB_URL := ftp://sources.redhat.com/pub/newlib/$(NEWLIB_FILE)

PCIUTILS_FILE := pciutils-2.2.9.tar.bz2
PCIUTILS_URL := http://www.kernel.org/pub/software/utils/pciutils/$(PCIUTILS_FILE)

ZLIB_FILE := zlib-1.2.3.tar.gz
ZLIB_URL := http://downloads.sourceforge.net/project/libpng/zlib/1.2.3/$(ZLIB_FILE)

OCAML_FILE := ocaml-3.11.0.tar.gz
OCAML_URL := http://caml.inria.fr/pub/distrib/ocaml-3.11/$(OCAML_FILE)

GC_FILE = gc.tar.gz
GC_URL := http://xenbits.xensource.com/xen-extfiles/$(GC_FILE)

VTPM_FILE := tpm_emulator-0.7.4.tar.gz
VTPM_URL := http://sourceforge.net/projects/tpm-emulator.berlios/files/$(VTPM_FILE)

GMP_FILE := gmp-4.3.2.tar.bz2
GMP_URL := ftp://ftp.gmplib.org/pub/gmp-4.3.2/$(GMP_FILE)
GMP_SIGN_SUFF := .sig

POLARSSL_FILE := polarssl-1.1.4-gpl.tgz
POLARSSL_URL := http://polarssl.org/code/releases/$(POLARSSL_FILE)

TBOOT_FILE := tboot-20090330.tar.gz
TBOOT_URL := http://xenbits.xensource.com/xen-extfiles/tboot-20090330.tar.gz

URL := $(SRC_BASEURL)/$(SRC_FILE)
URL_SIGN := $(SRC_BASEURL)/$(SIGN_FILE)

ALL_FILES := $(SRC_FILE) $(SIGN_FILE) $(GRUB_FILE) $(GRUB_FILE)$(GRUB_SIGN_SUFF) $(LWIP_FILE) $(LWIP_FILE)$(LWIP_SIGN_SUFF) $(NEWLIB_FILE) $(PCIUTILS_FILE) $(ZLIB_FILE) $(OCAML_FILE) $(GC_FILE) $(VTPM_FILE) $(GMP_FILE) $(GMP_FILE)$(GMP_SIGN_SUFF) $(POLARSSL_FILE) $(TBOOT_FILE)

ALL_URLS := $(URL) $(URL_SIGN) $(GRUB_URL) $(GRUB_URL)$(GRUB_SIGN_SUFF) $(LWIP_URL) $(LWIP_URL)$(LWIP_SIGN_SUFF) $(NEWLIB_URL) $(PCIUTILS_URL) $(ZLIB_URL) $(OCAML_URL) $(GC_URL) $(VTPM_URL) $(GMP_URL) $(GMP_URL)$(GMP_SIGN_SUFF) $(POLARSSL_URL) $(TBOOT_URL)

ifneq ($(DISTFILES_MIRROR),)
ALL_URLS := $(addprefix $(DISTFILES_MIRROR),$(ALL_FILES))
endif

get-sources: $(ALL_FILES)

$(ALL_FILES):
	@wget -qN $(ALL_URLS)

import-keys:
	@if [ -n "$$GNUPGHOME" ]; then rm -f "$$GNUPGHOME/vmm-xen-trustedkeys.gpg"; fi
	@gpg --no-auto-check-trustdb --no-default-keyring --keyring vmm-xen-trustedkeys.gpg -q --import *-key.asc

verify-sources: import-keys verify-sources-sig verify-sources-sum

verify-sources-sig: $(SRC_FILE) $(GRUB_FILE) $(LWIP_FILE) $(GMP_FILE)
	@for f in $^; do gpgv --keyring vmm-xen-trustedkeys.gpg $$f.sig $$f 2>/dev/null || (echo "Wrong signature on $$f!"; exit 1); done

verify-sources-sum: $(NEWLIB_FILE) $(ZLIB_FILE) $(OCAML_FILE) $(GC_FILE) $(VTPM_FILE) $(TBOOT_FILE) $(PCIUTILS_FILE) $(POLARSSL_FILE)
	@for f in $^; do sha1sum --quiet -c $$f.sha1sum || exit 1; done


.PHONY: clean-sources
clean-sources:
ifneq ($(SRC_FILE), None)
	-rm $(SRC_FILE)
endif


#RPM := rpmbuild --buildroot=/dev/shm/buildroot/
RPM := rpmbuild 

RPM_WITH_DIRS = $(RPM) $(RPM_DEFINES)

rpms-vm:
	$(RPM_WITH_DIRS) -bb xen-vm.spec
	rpm --addsign $(RPMDIR)/x86_64/xen-qubes-vm*$(VERSION)-$(RELEASE)*.rpm

rpms-dom0: rpms

rpms: get-sources verify-sources $(SPECFILE)
	[ -d gui -a -d vchan ] || { echo "You must copy Qubes 'gui' and 'vchan' here to build Xen for HVM domain; it is done automatically by qubes-builder"; exit 1; }
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
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/current/dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(VERSION)gui*$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/current/dom0/rpm/
	for vmrepo in ../yum/current-release/current/vm/* ; do \
	    	dist=$$(basename $$vmrepo); \
		ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-devel-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-qubes-vm-essentials-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
	done

update-repo-current-testing:
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/current-testing/dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(VERSION)gui*$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/current-testing/dom0/rpm/
	for vmrepo in ../yum/current-release/current-testing/vm/* ; do \
	    	dist=$$(basename $$vmrepo); \
		ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-devel-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-qubes-vm-essentials-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
	done

update-repo-unstable:
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/unstable/dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(VERSION)gui*$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/unstable/dom0/rpm/
	for vmrepo in ../yum/current-release/unstable/vm/* ; do \
	    	dist=$$(basename $$vmrepo); \
		ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-devel-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-qubes-vm-essentials-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
	done

update-repo-template:
	for vmrepo in ../template-builder/yum_repo_qubes/* ; do \
		dist=$$(basename $$vmrepo) ;\
		ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-devel-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-qubes-vm-essentials-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
		ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/ ;\
	done

update-repo-installer:
	ln -f rpm/x86_64/xen-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-debuginfo-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-doc-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-hypervisor-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-runtime-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(VERSION)gui2*-$(RELEASE).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/

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
	@echo "make update-repo-current-testing  -- same, but to -current-testing repo"
	@echo "make update-repo-unstable -- same, but to -testing repo"
