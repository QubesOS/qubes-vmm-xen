ifeq ($(PACKAGE_SET),dom0)
  RPM_SPEC_FILES := xen.spec
  SOURCE_COPY_IN := source-xen-copy-in

else ifeq ($(PACKAGE_SET),vm)
  RPM_SPEC_FILES := xen-vm.spec
  ARCH_BUILD_DIRS := archlinux
  DEBIAN_BUILD_DIRS := debian-xen/debian

  ifeq ($(DISTRIBUTION),debian)
    SOURCE_COPY_IN := source-debian-xen-copy-in
  else ifeq ($(DISTRIBUTION),qubuntu)
    SOURCE_COPY_IN := source-xen-copy-in
  endif
endif

source-xen-copy-in:
	DIST_SRC="$(CHROOT_DIR)/$(DIST_SRC)" \
	DIST_SRC_ROOT="$(CHROOT_DIR)/$(DIST_SRC_ROOT)" \
	$(ORIG_SRC)/qubes-builder-pre-hook.sh

source-debian-xen-copy-in: VERSION = $(shell cat $(ORIG_SRC)/version)
source-debian-xen-copy-in: SRC_FILE = "$(CHROOT_DIR)/$(DIST_SRC)/xen-$(VERSION).tar.gz"
source-debian-xen-copy-in:
	$(ORIG_SRC)/debian-quilt $(ORIG_SRC)/series-debian-vm.conf $(CHROOT_DIR)/$(DIST_SRC)/debian-xen/debian/patches
	tar xvfz $(SRC_FILE) -C $(CHROOT_DIR)/$(DIST_SRC)/debian-xen --strip-components=1 
	mv $(SRC_FILE) $(CHROOT_DIR)/$(DIST_SRC)/qubes-xen_$(VERSION).orig.tar.gz

# vim: filetype=make
