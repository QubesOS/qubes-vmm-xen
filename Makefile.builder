RPM_SPEC_FILES.dom0 := xen.spec
RPM_SPEC_FILES.vm := xen.spec

ARCH_BUILD_DIRS.vm := archlinux

DEBIAN_BUILD_DIRS.vm.debian := debian-vm/debian
SOURCE_COPY_IN.vm.debian := source-debian-xen-copy-in

DEBIAN_BUILD_DIRS.vm.qubuntu := debian-vm/debian
SOURCE_COPY_IN.vm.qubuntu := source-debian-xen-copy-in


RPM_SPEC_FILES := $(RPM_SPEC_FILES.$(PACKAGE_SET))
ARCH_BUILD_DIRS := $(ARCH_BUILD_DIRS.$(PACKAGE_SET))

DEBIAN_BUILD_DIRS := $(DEBIAN_BUILD_DIRS.$(PACKAGE_SET).$(DISTRIBUTION))
SOURCE_COPY_IN := $(SOURCE_COPY_IN.$(PACKAGE_SET).$(DISTRIBUTION))

source-debian-xen-copy-in: VERSION = $(shell cat $(ORIG_SRC)/version)
source-debian-xen-copy-in: ORIG_FILE = "$(CHROOT_DIR)/$(DIST_SRC)/xen_$(VERSION).orig.tar.gz"
source-debian-xen-copy-in: SRC_FILE  = "$(CHROOT_DIR)/$(DIST_SRC)/xen-$(VERSION).tar.gz"
source-debian-xen-copy-in:
	-$(ORIG_SRC)/debian-quilt $(ORIG_SRC)/series-debian-vm.conf $(CHROOT_DIR)/$(DIST_SRC)/debian/patches
	tar xfz $(SRC_FILE) -C $(CHROOT_DIR)/$(DIST_SRC)/debian-vm --strip-components=1 
	tar cfz $(ORIG_FILE) --exclude-vcs --exclude=debian -C $(CHROOT_DIR)/$(DIST_SRC)/debian-vm .
