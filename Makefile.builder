ifeq ($(PACKAGE_SET),dom0)
  RPM_SPEC_FILES := xen.spec

else ifeq ($(PACKAGE_SET),vm)
  RPM_SPEC_FILES := xen.spec
  ARCH_BUILD_DIRS := archlinux

  ifneq ($(filter $(DISTRIBUTION), debian qubuntu),)
  DEBIAN_BUILD_DIRS := debian-vm/debian
    SOURCE_COPY_IN := source-debian-xen-copy-in
  endif
endif

NO_ARCHIVE := 1

source-debian-xen-copy-in: VERSION = $(shell cat $(ORIG_SRC)/version)
source-debian-xen-copy-in: ORIG_FILE = "$(CHROOT_DIR)/$(DIST_SRC)/xen_$(VERSION).orig.tar.gz"
source-debian-xen-copy-in: SRC_FILE  = "$(CHROOT_DIR)/$(DIST_SRC)/xen-$(VERSION).tar.gz"
source-debian-xen-copy-in:
	-$(ORIG_SRC)/debian-quilt $(ORIG_SRC)/series-debian-vm.conf $(CHROOT_DIR)/$(DIST_SRC)/debian/patches
	tar xfz $(SRC_FILE) -C $(CHROOT_DIR)/$(DIST_SRC)/debian-vm --strip-components=1 
	rm -f $(CHROOT_DIR)/$(DIST_SRC)/debian-vm/rel
	rm -f $(CHROOT_DIR)/$(DIST_SRC)/debian-vm/version
	cp $(SRC_FILE) $(ORIG_FILE)
