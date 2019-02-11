ETC_SCRIPTS = \
	qemu-ifup

GLOBAL_SCRIPTS = \
	xen

GLOBAL_TOOLSTACK_LINKS = \
	xl \
	xm

GLOBAL_TOOLSTACK_WRAPPER = xen-toolstack-wrapper

GLOBAL_UTILS_LINKS = \
	xenperf \
	xenpm \
	xentop \
	xentrace \
	xentrace_format \
	xentrace_setmask \
	xentrace_setsize

GLOBAL_UTILS_WRAPPER = xen-utils-wrapper

ETC_SCRIPTS_DIR = /etc/xen/scripts
GLOBAL_SCRIPTS_DIR = /usr/sbin
PRIVATE_SCRIPTS_DIR = /usr/lib/xen-common/bin

install:
	install -d $(DESTDIR)$(ETC_SCRIPTS_DIR)
	install $(ETC_SCRIPTS) $(DESTDIR)$(ETC_SCRIPTS_DIR)
	install -d $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)
	install $(GLOBAL_SCRIPTS) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)
	@for i in $(GLOBAL_TOOLSTACK_LINKS); do \
	    echo ln -s $(PRIVATE_SCRIPTS_DIR)/$(GLOBAL_TOOLSTACK_WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i; \
	    ln -s $(PRIVATE_SCRIPTS_DIR)/$(GLOBAL_TOOLSTACK_WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i || exit 1; \
        done
	@for i in $(GLOBAL_UTILS_LINKS); do \
	    echo ln -s $(PRIVATE_SCRIPTS_DIR)/$(GLOBAL_UTILS_WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i; \
	    ln -s $(PRIVATE_SCRIPTS_DIR)/$(GLOBAL_UTILS_WRAPPER) $(DESTDIR)$(GLOBAL_SCRIPTS_DIR)/$$i || exit 1; \
	done
	install -d $(DESTDIR)$(PRIVATE_SCRIPTS_DIR)
