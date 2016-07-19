#
# Common Makefile for building RPMs
#

NAME := xen
SPECFILE := xen.spec

_sourcedir := $(shell pwd)
_specdir := $(if $(SPECDIR), $(SPECDIR), $(_sourcedir))
_builddir := $(if $(BUILDDIR), $(BUILDDIR), $(_sourcedir))
_srcrpmdir := $(if $(SRCRPMDIR), $(SRCRPMDIR), $(_sourcedir)/srpm)
_rpmdir := $(if $(RPMDIR), $(RPMDIR), $(_sourcedir)/rpm)
version := $(shell cat version)
release := $(shell cat rel)
jobs := $(shell grep -c ^processor /proc/cpuinfo)

def = --define "$(v) $(value $(v))"
RPM_DEFINES := $(foreach v, _sourcedir _specdir _builddir _srcrpmdir _rpmdir version jobs, $(def))

DIST_DOM0 ?= fc13

#DISTFILES_MIRROR := http://ftp.qubes-os.org/distfiles/

ifndef version
$(error "You can not run this Makefile without having version defined")
endif
ifndef release
$(error "You can not run this Makefile without having release defined")
endif

all: help

UNTRUSTED_SUFF := .UNTRUSTED

# All the URLs we need to fetch. URLS ending in .sig result in fetching the
# signature file _and_ the file it signs for (assumed to be the basename).
URLS := \
    http://bits.xensource.com/oss-xen/release/${version}/xen-${version}.tar.gz.sig \
    ftp://alpha.gnu.org/gnu/grub/grub-0.97.tar.gz.sig \
    http://download.savannah.gnu.org/releases/lwip/older_versions/lwip-1.3.0.tar.gz.sig \
    ftp://sources.redhat.com/pub/newlib/newlib-1.16.0.tar.gz \
    http://www.kernel.org/pub/software/utils/pciutils/pciutils-2.2.9.tar.bz2 \
    http://downloads.sourceforge.net/project/libpng/zlib/1.2.3/zlib-1.2.3.tar.gz \
    http://caml.inria.fr/pub/distrib/ocaml-3.11/ocaml-3.11.0.tar.gz \
    http://xenbits.xensource.com/xen-extfiles/gc.tar.gz \
    http://sourceforge.net/projects/tpm-emulator.berlios/files/tpm_emulator-0.7.4.tar.gz \
    ftp://ftp.gmplib.org/pub/archive/gmp-4.3.2/gmp-4.3.2.tar.bz2.sig \
    http://polarssl.org/code/releases/polarssl-1.1.4-gpl.tgz \
    http://xenbits.xensource.com/xen-extfiles/tboot-20090330.tar.gz

ALL_FILES := $(notdir $(URLS:%.sig=%)) $(notdir $(filter %.sig, $(URLS)))
ALL_URLS := $(URLS:%.sig=%) $(filter %.sig, $(URLS))

ifneq ($(DISTFILES_MIRROR),)
ALL_URLS := $(addprefix $(DISTFILES_MIRROR),$(ALL_FILES))
endif

get-sources: $(ALL_FILES)
	git submodule update --init --recursive

keyring := vmm-xen-trustedkeys.gpg
keyring-file := $(if $(GNUPGHOME), $(GNUPGHOME)/, $(HOME)/.gnupg/)$(keyring)
keyring-import := gpg -q --no-auto-check-trustdb --no-default-keyring --import

$(keyring-file): $(wildcard *.asc)
	@rm -f $(keyring-file) && $(keyring-import) --keyring $(keyring) $^

# get-sources already handle verification and remove the file(s) when it fails.
# Keep verify-sources target present for compatibility with qubes-builder API.
verify-sources:
	@true

$(filter %.sig, $(ALL_FILES)): %:
	@wget --no-use-server-timestamps -q -O $@ $(filter %$@,$(ALL_URLS))

%: %.sig $(keyring-file)
	@wget --no-use-server-timestamps -q -O $@$(UNTRUSTED_SUFF) $(filter %$@,$(ALL_URLS))
	@gpgv --keyring vmm-xen-trustedkeys.gpg $< $@$(UNTRUSTED_SUFF) 2>/dev/null || \
		{ echo "Wrong signature on $@$(UNTRUSTED_SUFF)!"; exit 1; }
	@mv $@$(UNTRUSTED_SUFF) $@

%: %.sha1sum
	@wget --no-use-server-timestamps -q -O $@$(UNTRUSTED_SUFF) $(filter %$@,$(ALL_URLS))
	@sha1sum --status -c $< <$@$(UNTRUSTED_SUFF) || \
		{ echo "Wrong SHA1 checksum on $@$(UNTRUSTED_SUFF)!"; exit 1; }
	@mv $@$(UNTRUSTED_SUFF) $@

.PHONY: clean-sources
clean-sources:
	rm -f $(ALL_FILES) *$(UNTRUSTED_SUFF)

RPMBUILD = rpmbuild $(RPM_DEFINES)

rpms-vm:
	$(RPMBUILD) -bb xen-vm.spec
	rpm --addsign $(_rpmdir)/x86_64/xen-qubes-vm*$(version)-$(release)*.rpm

rpms-dom0: rpms

rpms: get-sources verify-sources $(SPECFILE)
	[ -d gui -a -d vchan ] || { echo "You must copy Qubes 'gui' and 'vchan' here to build Xen for HVM domain; it is done automatically by qubes-builder"; exit 1; }
	$(RPMBUILD) -bb $(SPECFILE)
	rpm --addsign $(_rpmdir)/x86_64/*$(version)-$(release)*.rpm

rpms-nobuild:
	$(RPMBUILD) --nobuild -bb $(SPECFILE)

rpms-just-build:
	$(RPMBUILD) --short-circuit -bc $(SPECFILE)

rpms-install:
	$(RPMBUILD) -bi $(SPECFILE)

prep: get-sources $(SPECFILE)
	$(RPMBUILD) -bp $(SPECFILE)

srpm: get-sources $(SPECFILE)
	$(RPMBUILD) -bs $(SPECFILE)

verrel:
	@echo $(NAME)-$(version)-$(release)

.PHONY: clean
clean::
	@echo "Running the %clean script of the rpmbuild..."
	-$(RPMBUILD) --clean --nodeps $(SPECFILE)

define make-repo-links
    dist=`basename $$vmrepo`;\
    ln -f rpm/x86_64/xen-libs-$(version)-$(release).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-devel-$(version)-$(release).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-qubes-vm-essentials-$(version)-$(release).$$dist*.rpm $$vmrepo/rpm/;\
    ln -f rpm/x86_64/xen-licenses-$(version)-$(release).$$dist*.rpm $$vmrepo/rpm/
endef

update-repo.%: repo = $(subst .,,$(suffix $@))
update-repo.%:
	ln -f rpm/x86_64/*$(version)-$(release).$(DIST_DOM0)*.rpm ../yum/current-release/$(repo)/dom0/rpm/
	ln -f rpm/x86_64/xen-hvm-$(version)gui*$(release).$(DIST_DOM0)*.rpm ../yum/current-release/$(repo)/dom0/rpm/
	for vmrepo in ../yum/current-release/$(repo)/vm/*; do $(make-repo-links); done

update-repo-current: update-repo.current
update-repo-current-testing: update-repo.current-testing
update-repo-unstable: update-repo.unstable

update-repo-template:
	for vmrepo in ../template-builder/yum_repo_qubes/*; do $(make-repo-links); done

xen-pkg-names := xen xen-debuginfo xen-doc xen-hypervisor xen-libs xen-runtime xen-licenses
xen-pkgs := $(xen-pkg-names:%=%-$(version)-$(release).$(DIST_DOM0))

update-repo-installer:
	for pkg in $(xen-pkgs); do ln -f rpm/x86_64/$$pkg*.rpm ../installer/yum/qubes-dom0/rpm/; done
	ln -f rpm/x86_64/xen-hvm-$(version)gui2*-$(release).$(DIST_DOM0)*.rpm ../installer/yum/qubes-dom0/rpm/

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
