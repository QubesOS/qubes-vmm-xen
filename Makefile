VERSION := $(file <version)

#DISTFILES_MIRROR ?= http://ftp.qubes-os.org/distfiles/

all:
	@true

UNTRUSTED_SUFF := .UNTRUSTED

# All the URLs we need to fetch. URLS ending in .sig result in fetching the
# signature file _and_ the file it signs for (assumed to be the basename).
URLS := \
    https://downloads.xenproject.org/release/xen/$(VERSION)/xen-$(VERSION).tar.gz.sig

ALL_FILES := $(notdir $(URLS:%.sig=%)) $(notdir $(filter %.sig, $(URLS)))
ALL_URLS := $(URLS:%.sig=%) $(filter %.sig, $(URLS))

ifneq ($(DISTFILES_MIRROR),)
ALL_URLS := $(addprefix $(DISTFILES_MIRROR),$(ALL_FILES))
endif

SHELL := bash

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

ifeq ($(FETCH_CMD),)
$(error "You can not run this Makefile without having FETCH_CMD defined")
endif

$(filter %.sig, $(ALL_FILES)): %:
	@$(FETCH_CMD) $@ $(filter %$@,$(ALL_URLS))

%: %.sig $(keyring-file)
	@$(FETCH_CMD) $@$(UNTRUSTED_SUFF) $(filter %$@,$(ALL_URLS))
	@gpgv --keyring vmm-xen-trustedkeys.gpg $< $@$(UNTRUSTED_SUFF) 2>/dev/null || \
		{ echo "Wrong signature on $@$(UNTRUSTED_SUFF)!"; exit 1; }
	@mv $@$(UNTRUSTED_SUFF) $@

%: %.sha512
	@$(FETCH_CMD) $@$(UNTRUSTED_SUFF) $(filter %$@,$(ALL_URLS))
	@sha512sum --status -c <(printf "$$(cat $<)  -\n") <$@$(UNTRUSTED_SUFF) || \
		{ echo "Wrong SHA512 checksum on $@$(UNTRUSTED_SUFF)!"; exit 1; }
	@mv $@$(UNTRUSTED_SUFF) $@

.PHONY: clean-sources
clean-sources:
	rm -f $(ALL_FILES) *$(UNTRUSTED_SUFF)

.PHONY: clean
clean::
	rm -rf pkgs
	rm -rf debian/changelog.*
