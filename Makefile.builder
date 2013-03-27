ifeq ($(PACKAGE_SET),dom0)
RPM_SPEC_FILES := xen.spec
SOURCE_COPY_IN := source-xen-copy-in
else ifeq ($(PACKAGE_SET),vm)
RPM_SPEC_FILES := xen-vm.spec
ARCH_BUILD_DIRS := archlinux
endif

source-xen-copy-in:
	DIST_SRC="$(CHROOT_DIR)/$(DIST_SRC)" \
	DIST_SRC_ROOT="$(CHROOT_DIR)/$(DIST_SRC_ROOT)" \
	$(ORIG_SRC)/qubes-builder-pre-hook.sh
