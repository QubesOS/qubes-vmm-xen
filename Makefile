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

DISTFILES_MIRROR := http://ftp.qubes-os.org/distfiles/
NO_OF_CPUS := $(shell grep -c ^processor /proc/cpuinfo)

RPM_DEFINES := --define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SPECDIR)" \
		--define "_builddir $(BUILDDIR)" \
		--define "_srcrpmdir $(SRCRPMDIR)" \
		--define "_rpmdir $(RPMDIR)" \
		--define "version $(VERSION)" \
		--define "jobs $(NO_OF_CPUS)"

ifndef VERSION
$(error "You can not run this Makefile without having VERSION defined")
endif
ifndef RELEASE
$(error "You can not run this Makefile without having RELEASE defined")
endif

all: help

URLS := \
    http://bits.xensource.com/oss-xen/release/${VERSION}/xen-${VERSION}.tar.gz.sig \
    ftp://alpha.gnu.org/gnu/grub/grub-0.97.tar.gz.sig \
    http://download.savannah.gnu.org/releases/lwip/older_versions/lwip-1.3.0.tar.gz.sig \
    ftp://sources.redhat.com/pub/newlib/newlib-1.16.0.tar.gz \
    http://www.kernel.org/pub/software/utils/pciutils/pciutils-2.2.9.tar.bz2 \
    http://downloads.sourceforge.net/project/libpng/zlib/1.2.3/zlib-1.2.3.tar.gz \
    http://caml.inria.fr/pub/distrib/ocaml-3.11/ocaml-3.11.0.tar.gz \
    http://xenbits.xensource.com/xen-extfiles/gc.tar.gz \
    http://sourceforge.net/projects/tpm-emulator.berlios/files/tpm_emulator-0.7.4.tar.gz \
    ftp://ftp.gmplib.org/pub/gmp-4.3.2/gmp-4.3.2.tar.bz2.sig \
    http://polarssl.org/code/releases/polarssl-1.1.4-gpl.tgz \
    http://xenbits.xensource.com/xen-extfiles/tboot-20090330.tar.gz

ALL_FILES := $(notdir $(URLS:%.sig=%)) $(notdir $(filter %.sig, $(URLS)))
ALL_URLS := $(URLS:%.sig=%) $(filter %.sig, $(URLS))

ifneq ($(DISTFILES_MIRROR),)
ALL_URLS := $(addprefix $(DISTFILES_MIRROR),$(ALL_FILES))
endif

get-sources: $(ALL_FILES)
	git submodule update --init --recursive

$(ALL_FILES):
	@wget -qN $(ALL_URLS)

keyring := vmm-xen-trustedkeys.gpg
keyring-file := $(if $(GNUPGHOME), $(GNUPGHOME)/, $(HOME)/.gnupg/)$(keyring)
keyring-import:= gpg -q --no-auto-check-trustdb --no-default-keyring --import

$(keyring-file): $(wildcard *.asc)
	@rm -f $(keyring-file) && $(keyring-import) --keyring $(keyring) $^

%.verified: %.sig % $(keyring-file)
	@gpgv --keyring $(keyring) $< $* >/dev/null 2>&1 && touch $@

%.verified: %.sha1sum %
	@sha1sum --quiet -c $< && touch $@

verify-sources: $(filter-out %.sig.verified, $(ALL_FILES:%=%.verified))

.PHONY: clean-sources
clean-sources:
	-rm xen-${VERSION}.tar.gz


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

define make-repo-links
    dist=`basename $$vmrepo`;\
    ln -f rpm/x86_64/xen-libs-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-devel-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-qubes-vm-essentials-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-licenses-$(VERSION)-$(RELEASE).$$dist*.rpm $$vmrepo/rpm/
endef

update-repo.%: repo = $(subst .,,$(suffix $@))
update-repo.%:
	ln -f rpm/x86_64/*$(VERSION)-$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/$(repo)/dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(VERSION)gui*$(RELEASE).$(DIST_DOM0)*.rpm ../yum/current-release/$(repo)/dom0/rpm/
	for vmrepo in ../yum/current-release/$(repo)/vm/* ; do $(make-repo-links); done

update-repo-current: update-repo.current
update-repo-current-testing: update-repo.current-testing
update-repo-unstable: update-repo.unstable

update-repo-template:
	for vmrepo in ../template-builder/yum_repo_qubes/* ; do $(make-repo-links); done

xen-pkg-names := xen xen-debuginfo xen-doc xen-hypervisor xen-libs xen-runtime xen-licenses
xen-pkgs := $(xen-pkg-names:%=%-$(VERSION)-$(RELEASE).$(DIST_DOM0))

update-repo-installer:
	for pkg in $(xen-pkgs); do ln -f rpm/x86_64/$$pkg*.rpm ../installer/yum/qubes-dom0/rpm/; done
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
