ifeq ($(BACKEND_VMM),xen)
ifeq ($(PACKAGE_SET),dom0)
  RPM_SPEC_FILES := xen.spec

else ifeq ($(PACKAGE_SET),vm)
  ARCH_BUILD_DIRS := archlinux
  ifneq ($(filter $(DIST),centos8 centos-stream8),)
  RPM_SPEC_FILES := xen.spec
  endif
endif
endif

NO_ARCHIVE := 1
