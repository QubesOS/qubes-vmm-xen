%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# Hypervisor ABI
%define hv_abi  4.1

%define dist .qubes
%{!?version: %define version %(cat version)}
%{!?rel: %define rel %(cat rel)}

Summary: Xen is a virtual machine monitor
Name:    xen
Version: %{version}
Release: %{rel}%{?dist}
Epoch:   1000
Group:   Development/Libraries
License: GPLv2+ and LGPLv2+ and BSD
URL:     http://xen.org/
Source0: xen-%{version}.tar.gz
Source1: %{name}.modules
Source2: %{name}.logrotate
# used by stubdoms
Source10: lwip-1.3.0.tar.gz
Source11: newlib-1.16.0.tar.gz
Source12: zlib-1.2.3.tar.gz
Source13: pciutils-2.2.9.tar.bz2
Source14: grub-0.97.tar.gz
Source15: ipxe-git-v1.0.0.tar.gz
Source16: ocaml-3.11.0.tar.gz
Source17: gc.tar.gz
Source18: tpm_emulator-0.5.1.tar.gz
Source19: tboot-20090330.tar.gz
# init.d bits
Source20: init.xenstored
Source21: init.xenconsoled
Source22: init.blktapctrl
Source23: init.xend
# sysconfig bits
Source30: sysconfig.xenstored
Source31: sysconfig.xenconsoled
Source32: sysconfig.blktapctrl

Patch1: xen-initscript.patch
Patch4: xen-dumpdir.patch
Patch5: xen-net-disable-iptables-on-bridge.patch

Patch10: xen-no-werror.patch

Patch18: localgcc45fix.patch
Patch20: localgcc451fix.patch
Patch23: grub-ext4-support.patch
Patch26: localgcc46fix.patch
Patch28: pygrubfix.patch

Patch100: xen-configure-xend.patch
Patch101: xen-no-downloads.patch

# libxl fixes
# 102-109,112-113,117 are candidates to be included in upstream release
Patch105: xen-xl-networkattach-memory-allocation.patch
Patch106: xen-libxl-python-missing-pyincref.patch
Patch108: xen-libxl-devid-to-nic-domid.patch
Patch110: xen-libxl-script-block-backend.patch
Patch111: xen-hotplug-external-store.patch
Patch112: xen-libxl-add-all-pci-at-once.patch
Patch113: xen-libxl-pci-detach-fix.patch
Patch114: xen-libxl-pci-list-segv-fix.patch
Patch115: xen-libxl-backend-xenstore-perms.patch
Patch116: xen-shared-loop-fix.patch
Patch117: xen-libxl-networkattach-empty-vif-dir.patch
Patch120: xen-libxl-block-attach-fix-non-dom0-backend.patch
Patch121: xen-libxl-daemon-pid-stderr.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: transfig libidn-devel zlib-devel texi2html SDL-devel curl-devel
BuildRequires: libX11-devel python-devel ghostscript tetex-latex
BuildRequires: ncurses-devel gtk2-devel libaio-devel
# for the docs
BuildRequires: perl texinfo
# so that the makefile knows to install udev rules
BuildRequires: udev
%ifnarch ia64
# so that x86_64 builds pick up glibc32 correctly
BuildRequires: /usr/include/gnu/stubs-32.h
# for the VMX "bios"
BuildRequires: dev86
%endif
BuildRequires: gettext
BuildRequires: gnutls-devel
BuildRequires: openssl-devel
# For ioemu PCI passthrough
BuildRequires: pciutils-devel
# Several tools now use uuid
BuildRequires: libuuid-devel
# iasl needed to build hvmloader
BuildRequires: iasl
# modern compressed kernels
BuildRequires: bzip2-devel xz-devel
# libfsimage
BuildRequires: e2fsprogs-devel
Requires: bridge-utils
Requires: PyXML
Requires: udev >= 059
Requires: xen-runtime = %{version}-%{release}
# Not strictly a dependency, but kpartx is by far the most useful tool right
# now for accessing domU data from within a dom0 so bring it in when the user
# installs xen.
Requires: kpartx
Requires: chkconfig
ExclusiveArch: %{ix86} x86_64 ia64
#ExclusiveArch: %{ix86} x86_64 ia64 noarch

%description
This package contains the XenD daemon and xm command line
tools, needed to manage virtual machines running under the
Xen hypervisor

%package libs
Summary: Libraries for Xen tools
Group: Development/Libraries
Requires(pre): /sbin/ldconfig
Requires(post): /sbin/ldconfig
Requires: xen-licenses
Provides: xen-libs = %{version}-%{release}

%description libs
This package contains the libraries needed to run applications
which manage Xen virtual machines.

%package qubes-vm-essentials
Summary: Minimal xen-runtime to be installed inside Qubes VMs
Requires: xen-libs = %{version}-%{release}
AutoReq: 0
%description qubes-vm-essentials
Just a few xenstore-* tools and hotplug scripts needed by Qubes VMs (including netvm)


%package runtime
Summary: Core Xen runtime environment
Group: Development/Libraries
Requires: xen-libs = %{version}-%{release}
Requires: /usr/bin/qemu-img /usr/bin/qemu-nbd
Requires: python-lxml
# Ensure we at least have a suitable kernel installed, though we can't
# force user to actually boot it.
Requires: xen-hypervisor-abi = %{hv_abi}
Provides: xen-runtime = %{version}-%{release}

%description runtime
This package contains the runtime programs and daemons which
form the core Xen userspace environment.


%package hypervisor
Summary: Libraries for Xen tools
Group: Development/Libraries
Provides: xen-hypervisor-abi = %{hv_abi}

%description hypervisor
This package contains the Xen hypervisor


%package doc
Summary: Xen documentation
Group: Documentation
#BuildArch: noarch

%description doc
This package contains the Xen documentation.


%package devel
Summary: Development libraries for Xen tools
Group: Development/Libraries
Requires: xen-libs = %{version}-%{release}

%description devel
This package contains what's needed to develop applications
which manage Xen virtual machines.


%package licenses
Summary: License files from Xen source
Group: Documentation

%description licenses
This package contains the license files from the source used
to build the xen packages.


%prep
%setup -q
%patch1 -p1
%patch4 -p1
%patch5 -p1

%patch10 -p1

%patch18 -p1
%patch20 -p1
%patch26 -p1
%patch28 -p1

%patch100 -p1
%patch101 -p1

%patch105 -p1
%patch106 -p1
%patch108 -p1
%patch110 -p1
%patch111 -p1
%patch112 -p1
%patch113 -p1
%patch114 -p1
%patch115 -p1
%patch116 -p1
%patch117 -p1
%patch120 -p1
%patch121 -p1

# stubdom sources
cp -v %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13} %{SOURCE14} %{SOURCE16} stubdom
cp -v %{PATCH23} stubdom/grub.patches/99grub-ext4-support.patch
cp -v %{SOURCE15} tools/firmware/etherboot/ipxe.tar.gz
cp -v %{SOURCE17} tools/vnet/
cp -v %{SOURCE18} tools/vtpm/

mkdir -p tboot
cp -v %{SOURCE19} tboot/

%build
export XEN_VENDORVERSION="-%{release}"
export CFLAGS="$RPM_OPT_FLAGS"
export OCAML_TOOLS=n
make %{?_smp_mflags} prefix=/usr dist-xen
make %{?_smp_mflags} prefix=/usr dist-tools
make                 prefix=/usr dist-docs
unset CFLAGS
make dist-stubdom


%install
rm -rf %{buildroot}
export OCAML_TOOLS=n
make DESTDIR=%{buildroot} prefix=/usr install-xen
make DESTDIR=%{buildroot} prefix=/usr install-tools
make DESTDIR=%{buildroot} prefix=/usr install-docs
make DESTDIR=%{buildroot} prefix=/usr install-stubdom

############ debug packaging: list files ############

find %{buildroot} -print | xargs ls -ld | sed -e 's|.*%{buildroot}||' > f1.list

############ kill unwanted stuff ############

# stubdom: newlib
rm -rf %{buildroot}/usr/*-xen-elf

# hypervisor symlinks
rm -rf %{buildroot}/boot/xen-4.1.gz
rm -rf %{buildroot}/boot/xen-4.gz

# silly doc dir fun
rm -fr %{buildroot}%{_datadir}/doc/xen
rm -rf %{buildroot}%{_datadir}/doc/qemu

# Pointless helper
rm -f %{buildroot}%{_sbindir}/xen-python-path

# qemu stuff (unused or available from upstream)
rm -rf %{buildroot}/usr/share/xen/man
rm -rf %{buildroot}/usr/bin/qemu-*-xen
ln -s qemu-img %{buildroot}/%{_bindir}/qemu-img-xen
ln -s qemu-img %{buildroot}/%{_bindir}/qemu-nbd-xen
for file in bios.bin openbios-sparc32 openbios-sparc64 ppc_rom.bin \
         pxe-e1000.bin pxe-ne2k_pci.bin pxe-pcnet.bin pxe-rtl8139.bin \
         vgabios.bin vgabios-cirrus.bin video.x openbios-ppc bamboo.dtb
do
	rm -f %{buildroot}/%{_datadir}/xen/qemu/$file
done

# README's not intended for end users
rm -f %{buildroot}/%{_sysconfdir}/xen/README*

# standard gnu info files
rm -rf %{buildroot}/usr/info

# adhere to Static Library Packaging Guidelines
rm -rf %{buildroot}/%{_libdir}/*.a

############ fixup files in /etc ############

# udev
#rm -rf %{buildroot}/etc/udev/rules.d/xen*.rules
#mv %{buildroot}/etc/udev/xen*.rules %{buildroot}/etc/udev/rules.d

# modules
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/modules
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/modules/%{name}.modules

# logrotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# init scripts
#mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
#mv %{buildroot}%{_sysconfdir}/init.d/* %{buildroot}%{_sysconfdir}/rc.d/init.d
#rmdir %{buildroot}%{_sysconfdir}/init.d
install -m 755 %{SOURCE20} %{buildroot}%{_sysconfdir}/rc.d/init.d/xenstored
install -m 755 %{SOURCE21} %{buildroot}%{_sysconfdir}/rc.d/init.d/xenconsoled
install -m 755 %{SOURCE22} %{buildroot}%{_sysconfdir}/rc.d/init.d/blktapctrl
install -m 755 %{SOURCE23} %{buildroot}%{_sysconfdir}/rc.d/init.d/xend

# sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE30} %{buildroot}%{_sysconfdir}/sysconfig/xenstored
install -m 644 %{SOURCE31} %{buildroot}%{_sysconfdir}/sysconfig/xenconsoled
install -m 644 %{SOURCE32} %{buildroot}%{_sysconfdir}/sysconfig/blktapctrl

# config file only used for hotplug, Fedora uses udev instead
rm -f %{buildroot}/%{_sysconfdir}/sysconfig/xend

############ create dirs in /var ############

mkdir -p %{buildroot}%{_localstatedir}/lib/xen/xend-db/domain
mkdir -p %{buildroot}%{_localstatedir}/lib/xen/xend-db/vnet
mkdir -p %{buildroot}%{_localstatedir}/lib/xen/xend-db/migrate
mkdir -p %{buildroot}%{_localstatedir}/lib/xen/images
mkdir -p %{buildroot}%{_localstatedir}/log/xen/console

############ create symlink for x86_64 for compatibility with 3.4 ############

%if "%{_libdir}" != "/usr/lib"
ln -s /usr/lib/%{name}/bin/qemu-dm %{buildroot}/%{_libdir}/%{name}/bin/qemu-dm
%endif

############ debug packaging: list files ############

find %{buildroot} -print | xargs ls -ld | sed -e 's|.*%{buildroot}||' > f2.list
diff -u f1.list f2.list || true

############ assemble license files ############

mkdir licensedir
# avoid licensedir to avoid recursion, also stubdom/ioemu and dist
# which are copies of files elsewhere
find . -path licensedir -prune -o -path stubdom/ioemu -prune -o \
  -path dist -prune -o -name COPYING -o -name LICENSE | while read file; do
  mkdir -p licensedir/`dirname $file`
  install -m 644 $file licensedir/$file
done

############ all done now ############

%post
/sbin/chkconfig --add xend
/sbin/chkconfig --add xendomains

if [ $1 != 0 ]; then
  service xend condrestart
fi

%preun
if [ $1 = 0 ]; then
  /sbin/chkconfig --del xend
  /sbin/chkconfig --del xendomains
fi

%post runtime
/sbin/chkconfig --add xenconsoled
/sbin/chkconfig --add xenstored
#/sbin/chkconfig --add blktapctrl

if [ $1 != 0 ]; then
  service xenconsoled condrestart
fi

%preun runtime
if [ $1 = 0 ]; then
  /sbin/chkconfig --del xenconsoled
  /sbin/chkconfig --del xenstored
  /sbin/chkconfig --del blktapctrl
fi

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

# Base package only contains XenD/xm python stuff
#files -f xen-xm.lang
%files
%defattr(-,root,root)
%doc COPYING README
%{_bindir}/xencons
%{_sbindir}/xend
%{_sbindir}/xm
%{python_sitearch}/%{name}
%{python_sitearch}/xen-*.egg-info
%{_mandir}/man1/xm.1*
%{_mandir}/man5/xend-config.sxp.5*
%{_mandir}/man5/xmdomain.cfg.5*
%{_datadir}/%{name}/create.dtd

# Startup script
%{_sysconfdir}/rc.d/init.d/xend
%{_sysconfdir}/rc.d/init.d/xendomains
# Guest config files
%config(noreplace) %{_sysconfdir}/%{name}/xmexample*
# Daemon config
%config(noreplace) %{_sysconfdir}/%{name}/xend-*
# xm config
%config(noreplace) %{_sysconfdir}/%{name}/xm-*
# Guest autostart links
%dir %attr(0700,root,root) %{_sysconfdir}/%{name}/auto
# Autostart of guests
%config(noreplace) %{_sysconfdir}/sysconfig/xendomains

# Persistent state for XenD
%dir %{_localstatedir}/lib/%{name}/xend-db/
%dir %{_localstatedir}/lib/%{name}/xend-db/domain
%dir %{_localstatedir}/lib/%{name}/xend-db/migrate
%dir %{_localstatedir}/lib/%{name}/xend-db/vnet

%files libs
%defattr(-,root,root)
%{_libdir}/*.so.*
%{_libdir}/fs

%files qubes-vm-essentials

%{_bindir}/xenstore
%{_bindir}/xenstore-*

# Hotplug rules
%config(noreplace) %{_sysconfdir}/udev/rules.d/*

%dir %attr(0700,root,root) %{_sysconfdir}/%{name}
%dir %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/
%config %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/*

# Auto-load xen backend drivers
%attr(0755,root,root) %{_sysconfdir}/sysconfig/modules/%{name}.modules

# Programs run by other programs
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/bin
%attr(0700,root,root) %{_libdir}/%{name}/bin/*

# General Xen state
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/dump
%dir %{_localstatedir}/lib/%{name}/images

# Xen logfiles
%dir %attr(0700,root,root) %{_localstatedir}/log/xen

# Python modules
%dir %{python_sitearch}/%{name}
%{python_sitearch}/%{name}/__init__.*
%{python_sitearch}/%{name}/lowlevel


# All runtime stuff except for XenD/xm python stuff
%files runtime
%defattr(-,root,root)
# Hotplug rules
%config(noreplace) %{_sysconfdir}/udev/rules.d/*

%dir %attr(0700,root,root) %{_sysconfdir}/%{name}
%dir %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/
%config %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/*

%{_sysconfdir}/rc.d/init.d/blktapctrl
%{_sysconfdir}/rc.d/init.d/xenstored
%{_sysconfdir}/rc.d/init.d/xenconsoled
%{_sysconfdir}/rc.d/init.d/xen-watchdog
%{_sysconfdir}/rc.d/init.d/xencommons
%{_sysconfdir}/bash_completion.d/xl.sh

%config(noreplace) %{_sysconfdir}/sysconfig/xenstored
%config(noreplace) %{_sysconfdir}/sysconfig/xenconsoled
%config(noreplace) %{_sysconfdir}/sysconfig/blktapctrl
%config(noreplace) %{_sysconfdir}/sysconfig/xencommons
%config(noreplace) %{_sysconfdir}/xen/xl.conf
%config(noreplace) %{_sysconfdir}/xen/cpupool

# Auto-load xen backend drivers
%attr(0755,root,root) %{_sysconfdir}/sysconfig/modules/%{name}.modules

# Rotate console log files
%config(noreplace) %{_sysconfdir}/logrotate.d/xen

# Programs run by other programs
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/bin
%attr(0700,root,root) %{_libdir}/%{name}/bin/*
# QEMU runtime files
%dir %{_datadir}/%{name}/qemu
%dir %{_datadir}/%{name}/qemu/keymaps
%{_datadir}/%{name}/qemu/keymaps/*

# man pages
%{_mandir}/man1/xentop.1*
%{_mandir}/man1/xentrace_format.1*
%{_mandir}/man8/xentrace.8*

%{python_sitearch}/fsimage.so
%{python_sitearch}/grub
%{python_sitearch}/pygrub-*.egg-info

# The firmware
%ifnarch ia64
# Avoid owning /usr/lib twice on i386
%if "%{_libdir}" != "/usr/lib"
%dir /usr/lib/%{name}
%dir /usr/lib/%{name}/bin
/usr/lib/%{name}/bin/stubdom-dm
/usr/lib/%{name}/bin/qemu-dm
/usr/lib/%{name}/bin/stubdompath.sh
%endif
%dir /usr/lib/%{name}/boot
# HVM loader is always in /usr/lib regardless of multilib
/usr/lib/xen/boot/hvmloader
/usr/lib/xen/boot/ioemu-stubdom.gz
/usr/lib/xen/boot/pv-grub*.gz
%endif
# General Xen state
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/dump
%dir %{_localstatedir}/lib/%{name}/images
# Xenstore persistent state
%dir %{_localstatedir}/lib/xenstored
# Xenstore runtime state
%ghost %{_localstatedir}/run/xenstored
# XenD runtime state
%ghost %attr(0700,root,root) %{_localstatedir}/run/xend
%ghost %attr(0700,root,root) %{_localstatedir}/run/xend/boot

# All xenstore CLI tools
%{_bindir}/qemu-*-xen
%{_bindir}/xenstore
%{_bindir}/xenstore-*
%{_bindir}/pygrub
%{_bindir}/xentrace*
%{_bindir}/remus
# blktap daemon
%{_sbindir}/blktapctrl
%{_sbindir}/tapdisk*
# XSM
%{_sbindir}/flask-*
# Disk utils
%{_sbindir}/qcow-create
%{_sbindir}/qcow2raw
%{_sbindir}/img2qcow
# Misc stuff
%{_bindir}/xen-detect
%{_sbindir}/gdbsx
%{_sbindir}/gtrace*
%{_sbindir}/kdd
%{_sbindir}/lock-util
%{_sbindir}/tap-ctl
%{_sbindir}/td-util
%{_sbindir}/vhd-*
%{_sbindir}/xen-bugtool
%{_sbindir}/xen-hptool
%{_sbindir}/xen-hvmcrash
%{_sbindir}/xen-hvmctx
%{_sbindir}/xen-tmem-list-parse
%{_sbindir}/xenconsoled
%{_sbindir}/xenlockprof
%{_sbindir}/xenmon.py*
%{_sbindir}/xenpaging
%{_sbindir}/xentop
%{_sbindir}/xentrace_setmask
%{_sbindir}/xenbaked
%{_sbindir}/xenstored
%{_sbindir}/xenpm
%{_sbindir}/xenpmd
%{_sbindir}/xenperf
%{_sbindir}/xenwatchdogd
%{_sbindir}/xl
%{_sbindir}/xsview

# Xen logfiles
%dir %attr(0700,root,root) %{_localstatedir}/log/xen
# Guest/HV console logs
%dir %attr(0700,root,root) %{_localstatedir}/log/xen/console

%files hypervisor
%defattr(-,root,root)
/boot/xen-syms-*
/boot/xen-*.gz
/boot/xen.gz

%files doc
%defattr(-,root,root)
%doc docs/misc/
%doc dist/install/usr/share/doc/xen/html
%doc dist/install/usr/share/doc/xen/pdf/*.pdf

%files devel
%defattr(-,root,root)
%{_includedir}/*.h
%dir %{_includedir}/xen
%{_includedir}/xen/*
%{_libdir}/*.so

%files licenses
%defattr(-,root,root)
%doc licensedir/*

%changelog
* Fri Mar 25 2011 Michael Young <m.a.young@durham.ac.uk> - 4.1.0-1
- update to 4.1.0 final

* Tue Mar 22 2011 Michael Young <m.a.young@durham.ac.uk> - 4.1.0-0.1.rc8
- update to 4.1.0-rc8 release candidate
- create xen-4.1.0-rc8.tar.xz file from git/hg repositories
- rebase xen-initscript.patch xen-dumpdir.patch
  xen-net-disable-iptables-on-bridge.patch localgcc45fix.patch
  sysconfig.xenstored init.xenstored
- remove unnecessary or conflicting xen-xenstore-cli.patch localpy27fixes.patch
  xen.irq.fixes.patch xen.xsave.disable.patch xen.8259afix.patch
  localcleanups.patch libpermfixes.patch
- add patch to allow pygrub to work with single partitions with boot sectors
- create ipxe-git-v1.0.0.tar.gz from http://git.ipxe.org/ipxe.git
  to avoid downloading at build time
- no need to move udev rules or init scripts as now created in the right place
- amend list of files shipped - remove fs-backend
  add init.d scripts xen-watchdog xencommons
  add config files xencommons xl.conf cpupool
  add programs kdd tap-ctl xen-hptool xen-hvmcrash xenwatchdogd

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-9
- Make libraries executable so that rpm gets dependencies right

* Sat Jan 29 2011 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-8
- Temporarily turn off some compile options so it will build on rawhide

* Fri Jan 28 2011 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-7
- ghost directories in /var/run (#656724)
- minor fixes to /usr/share/doc/xen-doc-4.?.?/misc/network_setup.txt (#653159)
  /etc/xen/scripts/network-route, /etc/xen/scripts/vif-common.sh (#669747)
  and /etc/sysconfig/modules/xen.modules (#656536)

* Tue Oct 12 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-6
- add upstream xen patch xen.8259afix.patch to fix boot panic
  "IO-APIC + timer doesn't work!" (#642108)

* Thu Oct 07 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-5
- add ext4 support for pvgrub (grub-ext4-support.patch from grub-0.97-66.fc14)

* Wed Sep 29 2010 jkeating - 4.0.1-4
- Rebuilt for gcc bug 634757

* Fri Sep 24 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-3
- create symlink for qemu-dm on x86_64 for compatibility with 3.4
- apply some patches destined for 4.0.2
    add some irq fixes
    disable xsave which causes problems for HVM

* Sun Aug 29 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-2
- fix compile problems on Fedora 15, I suspect due to gcc 4.5.1

* Wed Aug 25 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.1-1
- update to 4.0.1 release - many bug fixes
- xen-dev-create-cleanup.patch no longer needed
- remove part of localgcc45fix.patch no longer needed
- package new files /etc/bash_completion.d/xl.sh
  and /usr/sbin/gdbsx
- add patch to get xm and xend working with python 2.7

* Mon Aug 2 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.0-5
- add newer module names and xen-gntdev to xen.modules
- Update dom0-kernel.repo file to use repos.fedorapeople.org location

* Mon Jul 26 2010 Michael Young <m.a.young@durham.ac.uk>
- create a xen-licenses package to satisfy revised the Fedora
  Licensing Guidelines

* Sun Jul 25 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.0-4
- fix gcc 4.5 compile problems

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 4.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sun Jun 20 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.0-2
- add patch to remove some old device creation code that doesn't
  work with the latest pvops kernels

* Tue Jun 7 2010 Michael Young <m.a.young@durham.ac.uk> - 4.0.0-1
- update to 4.0.0 release
- rebase xen-initscript.patch and xen-dumpdir.patch patches
- adjust spec file for files added to or removed from the packages
- add new build dependencies libuuid-devel and iasl

* Tue Jun 1 2010 Michael Young <m.a.young@durham.ac.uk> - 3.4.3-1
- update to 3.4.3 release including
    support for latest pv_ops kernels (possibly incomplete)
    should fix build problems (#565063) and crashes (#545307)
- replace Prereq: with Requires: in spec file
- drop static libraries (#556101)

* Thu Dec 10 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.2-2
- adapt module load script to evtchn.ko -> xen-evtchn.ko rename.

* Thu Dec 10 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.2-1
- update to 3.4.2 release.
- drop backport patches.

* Fri Oct 8 2009 Justin M. Forbes <jforbes@redhat.com> - 3.4.1-5
- add PyXML to dependencies. (#496135)
- Take ownership of {_libdir}/fs (#521806)

* Mon Sep 14 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.1-4
- add e2fsprogs-devel to build dependencies.

* Tue Sep 2 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.1-3
- swap bzip2+xz linux kernel compression support patches.
- backport one more bugfix (videoram option).

* Tue Sep 1 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.1-2
- backport bzip2+xz linux kernel compression support.
- backport a few bugfixes.

* Fri Aug 7 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.1-1
- update to 3.4.1 release.

* Wed Aug 5 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.0-4
- Kill info files.  No xen docs, just standard gnu stuff.
- kill -Werror in tools/libxc to fix build.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu May 28 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.0-2
- rename info files to fix conflict with binutils.
- add install-info calls for the doc subpackage.
- un-parallelize doc build.

* Wed May 27 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.4.0-1
- update to version 3.4.0.
- cleanup specfile, add doc subpackage.

* Tue Mar 10 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-11
- fix python 2.6 warnings.

* Fri Mar 6 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-9
- fix xen.modules init script for pv_ops kernel.
- stick rpm release tag into XEN_VENDORVERSION.
- use %{ix86} macro in ExclusiveArch.
- keep blktapctrl turned off by default.

* Mon Mar 2 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-7
- fix xenstored init script for pv_ops kernel.

* Fri Feb 27 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-6
- fix xenstored crash.
- backport qemu-unplug patch.

* Tue Feb 24 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-5
- fix gcc44 build (broken constrain in inline asm).
- fix ExclusiveArch

* Tue Feb 3 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-3
- backport bzImage support for dom0 builder.

* Sun Jan 18 2009 Tomas Mraz <tmraz@redhat.com> - 3.3.1-2
- rebuild with new openssl

* Thu Jan 8 2009 Gerd Hoffmann <kraxel@redhat.com> - 3.3.1-1
- update to xen 3.3.1 release.

* Wed Dec 17 2008 Gerd Hoffmann <kraxel@redhat.com> - 3.3.0-2
- build and package stub domains (pvgrub, ioemu).
- backport unstable fixes for pv_ops dom0.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 3.3.0-1.1
- Rebuild for Python 2.6

* Fri Aug 29 2008 Daniel P. Berrange <berrange@redhat.com> - 3.3.0-1.fc10
- Update to xen 3.3.0 release

* Wed Jul 23 2008 Mark McLoughlin <markmc@redhat.com> - 3.2.0-17.fc10
- Enable xen-hypervisor build
- Backport support for booting DomU from bzImage
- Re-diff all patches for zero fuzz

* Wed Jul  9 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-16.fc10
- Remove bogus ia64 hypercall arg (rhbz #433921)

* Fri Jun 27 2008 Markus Armbruster <armbru@redhat.com> - 3.2.0-15.fc10
- Re-enable QEMU image format auto-detection, without the security
  loopholes

* Wed Jun 25 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-14.fc10
- Rebuild for GNU TLS ABI change

* Fri Jun 13 2008 Markus Armbruster <armbru@redhat.com> - 3.2.0-13.fc10
- Correctly limit PVFB size (CVE-2008-1952)

* Tue Jun  3 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-12.fc10
- Move /var/run/xend into xen-runtime for pygrub (rhbz #442052)

* Wed May 14 2008 Markus Armbruster <armbru@redhat.com> - 3.2.0-11.fc10
- Disable QEMU image format auto-detection (CVE-2008-2004)
- Fix PVFB to validate frame buffer description (CVE-2008-1943)

* Wed Feb 27 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-10.fc9
- Fix block device checks for extendable disk formats

* Wed Feb 27 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-9.fc9
- Let XenD setup QEMU logfile (rhbz #435164)
- Fix PVFB use of event channel filehandle

* Sat Feb 23 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-8.fc9
- Fix block device extents check (rhbz #433560)

* Mon Feb 18 2008 Mark McLoughlin <markmc@redhat.com> - 3.2.0-7.fc9
- Restore some network-bridge patches lost during 3.2.0 rebase

* Wed Feb  6 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-6.fc9
- Fixed xenstore-ls to automatically use xenstored socket as needed

* Sun Feb  3 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-5.fc9
- Fix timer mode parameter handling for HVM
- Temporarily disable all Latex docs due to texlive problems (rhbz #431327)

* Fri Feb  1 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-4.fc9
- Add a xen-runtime subpackage to allow use of Xen without XenD
- Split init script out to one script per daemon
- Remove unused / broken / obsolete tools

* Mon Jan 21 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-3.fc9
- Remove legacy dependancy on python-virtinst

* Mon Jan 21 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-2.fc9
- Added XSM header files to -devel RPM

* Fri Jan 18 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-1.fc9
- Updated to 3.2.0 final release

* Thu Jan 10 2008 Daniel P. Berrange <berrange@redhat.com> - 3.2.0-0.fc9.rc5.dev16701.1
- Rebase to Xen 3.2 rc5 changeset 16701

* Thu Dec 13 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.2-3.fc9
- Re-factor to make it easier to test dev trees in RPMs
- Include hypervisor build if doing a dev RPM

* Fri Dec 07 2007 Release Engineering <rel-eng@fedoraproject.org> - 3.1.2-2.fc9
- Rebuild for deps

* Sat Dec  1 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.2-1.fc9
- Upgrade to 3.1.2 bugfix release

* Sat Nov  3 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-14.fc9
- Disable network-bridge script since it conflicts with NetworkManager
  which is now on by default

* Fri Oct 26 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-13.fc9
- Fixed xenbaked tmpfile flaw (CVE-2007-3919)

* Wed Oct 10 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-12.fc8
- Pull in QEMU BIOS boot menu patch from KVM package
- Fix QEMU patch for locating x509 certificates based on command line args
- Add XenD config options for TLS x509 certificate setup

* Wed Sep 26 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-11.fc8
- Fixed rtl8139 checksum calculation for Vista (rhbz #308201)

* Wed Sep 26 2007 Chris Lalancette <clalance@redhat.com> - 3.1.0-10.fc8
- QEmu NE2000 overflow check - CVE-2007-1321
- Pygrub guest escape - CVE-2007-4993

* Mon Sep 24 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-9.fc8
- Fix generation of manual pages (rhbz #250791)
- Really fix FC-6 32-on-64 guests

* Mon Sep 24 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-8.fc8
- Make 32-bit FC-6 guest PVFB work on x86_64 host

* Mon Sep 24 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-7.fc8
- Re-add support for back-compat FC6 PVFB support
- Fix handling of explicit port numbers (rhbz #279581)

* Wed Sep 19 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-6.fc8
- Don't clobber the VIF type attribute in FV guests (rhbz #296061)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-5.fc8
- Added dep on openssl for blktap-qcow

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-4.fc8
- Switch PVFB over to use QEMU
- Backport QEMU VNC security patches for TLS/x509

* Wed Aug  1 2007 Markus Armbruster <armbru@redhat.com> - 3.1.0-3.fc8
- Put guest's native protocol ABI into xenstore, to provide for older
  kernels running 32-on-64.
- VNC keymap fixes
- Fix race conditions in LibVNCServer on client disconnect

* Tue Jun 12 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-2.fc8
- Remove patch which kills VNC monitor
- Fix HVM save/restore file path to be /var/lib/xen instead of /tmp
- Don't spawn a bogus xen-vncfb daemon for HVM guests
- Add persistent logging of hypervisor & guest consoles
- Add /etc/sysconfig/xen to allow admin choice of logging options
- Re-write Xen startup to use standard init script functions
- Add logrotate configuration for all xen related logs

* Fri May 25 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-1.fc8
- Updated to official 3.1.0 tar.gz
- Fixed data corruption from VNC client disconnect (bz 241303)

* Thu May 17 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-0.rc7.2.fc7
- Ensure xen-vncfb processes are cleanedup if guest quits (bz 240406)
- Tear down guest if device hotplug fails

* Thu May  3 2007 Daniel P. Berrange <berrange@redhat.com> - 3.1.0-0.rc7.1.fc7
- Updated to 3.1.0 rc7, changeset  15021 (upstream renumbered from 3.0.5)

* Tue May  1 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc4.4.fc7
- Fix op_save RPC API

* Mon Apr 30 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc4.3.fc7
- Added BR on gettext

* Mon Apr 30 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc4.2.fc7
- Redo failed build.

* Mon Apr 30 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc4.1.fc7
- Updated to 3.0.5 rc4, changeset 14993
- Reduce number of xenstore transactions used for listing domains
- Hack to pre-balloon 2 MB for PV guests as well as HVM

* Thu Apr 26 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc3.14934.2.fc7
- Fixed display of bootloader menu with xm create -c
- Added modprobe for both xenblktap & blktap to deal with rename issues
- Hack to pre-balloon 10 MB for HVM guests

* Thu Apr 26 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc3.14934.1.fc7
- Updated to 3.0.5 rc3, changeset 14934
- Fixed networking for service xend restart & minor IPv6 tweak

* Tue Apr 24 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc2.14889.2.fc7
- Fixed vfb/vkbd device startup race

* Tue Apr 24 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.5-0.rc2.14889.1.fc7
- Updated to xen 3.0.5 rc2, changeset 14889
- Remove use of netloop from network-bridge script
- Add backcompat support to vif-bridge script to translate xenbrN to ethN

* Wed Mar 14 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-9.fc7
- Disable access to QEMU monitor over VNC (CVE-2007-0998, bz 230295)

* Tue Mar  6 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-8.fc7
- Close QEMU file handles when running network script

* Fri Mar  2 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-7.fc7
- Fix interaction of bootloader with blktap (bz 230702)
- Ensure PVFB daemon terminates if domain doesn't startup (bz 230634)

* Thu Feb  8 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-6.fc7
- Setup readonly loop devices for readonly disks
- Extended error reporting for hotplug scripts
- Pass all 8 mouse buttons from VNC through to kernel

* Tue Jan 30 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-5.fc7
- Don't run the pvfb daemons for HVM guests (bz 225413)
- Fix handling of vnclisten parameter for HVM guests

* Tue Jan 30 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-4.fc7
- Fix pygrub memory corruption

* Tue Jan 23 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-3.fc7
- Added PVFB back compat for FC5/6 guests

* Mon Jan 22 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-2.fc7
- Ensure the arch-x86 header files are included in xen-devel package
- Bring back patch to move /var/xen/dump to /var/lib/xen/dump
- Make /var/log/xen mode 0700

* Thu Jan 11 2007 Daniel P. Berrange <berrange@redhat.com> - 3.0.4-1
- Upgrade to official xen-3.0.4_1 release tarball

* Thu Dec 14 2006 Jeremy Katz <katzj@redhat.com> - 3.0.3-3
- fix the build

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 3.0.3-2
- rebuild for python 2.5

* Tue Oct 24 2006 Daniel P. Berrange <berrange@redhat.com> - 3.0.3-1
- Pull in the official 3.0.3 tarball of xen (changeset 11774).
- Add patches for VNC password authentication (bz 203196)
- Switch /etc/xen directory to be mode 0700 because the config files
  can contain plain text passwords (bz 203196)
- Change the package dependency to python-virtinst to reflect the
  package name change.
- Fix str-2-int cast of VNC port for paravirt framebuffer (bz 211193)

* Wed Oct  4 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-44
- fix having "many" kernels in pygrub

* Wed Oct  4 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-43
- Fix SMBIOS tables for SVM guests [danpb] (bug 207501)

* Fri Sep 29 2006 Daniel P. Berrange <berrange@redhat.com> - 3.0.2-42
- Added vnclisten patches to make VNC only listen on localhost
  out of the box, configurable by 'vnclisten' parameter (bz 203196)

* Thu Sep 28 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-41
- Update to xen-3.0.3-testing changeset 11633

* Thu Sep 28 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-40
- Workaround blktap/xenstore startup race
- Add udev rules for xen blktap devices (srostedt)
- Add support for dynamic blktap device nodes (srostedt)
- Fixes for infinite dom0 cpu usage with blktap
- Fix xm not to die on malformed "tap:" blkif config string
- Enable blktap on kernels without epoll-for-aio support.
- Load the blktap module automatically at startup
- Reenable blktapctrl

* Wed Sep 27 2006 Daniel Berrange <berrange@redhat.com> - 3.0.2-39
- Disable paravirt framebuffer server side rendered cursor (bz 206313)
- Ignore SIGPIPE in paravirt framebuffer daemon to avoid terminating
  on client disconnects while writing data (bz 208025)

* Wed Sep 27 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-38
- Fix cursor in pygrub (#208041)

* Tue Sep 26 2006 Daniel P. Berrange <berrange@redhat.com> - 3.0.2-37
- Removed obsolete scary warnings in package description

* Thu Sep 21 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-36
- Add Requires: kpartx for dom0 access to domU data

* Wed Sep 20 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-35
- Don't strip qemu-dm early, so that we get proper debuginfo (danpb)
- Fix compile problem with latest glibc

* Wed Sep 20 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-34
- Update to xen-unstable changeset 11539
- Threading fixes for libVNCserver (danpb)

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-33
- update pvfb patch based on upstream feedback

* Tue Sep  5 2006 Juan Quintela <quintela@redhat.com> - 3.0.2-31
- re-enable ia64.

* Thu Aug 31 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-31
- update to changeset 11405

* Thu Aug 31 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-30
- fix pvfb for x86_64

* Wed Aug 30 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-29
- update libvncserver to hopefully fix problems with vnc clients disconnecting

* Tue Aug 29 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-28
- fix a typo

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-27
- add support for paravirt framebuffer

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-26
- update to xen-unstable cs 11251
- clean up patches some
- disable ia64 as it doesn't currently build 

* Tue Aug 22 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-25
- make initscript not spew on non-xen kernels (#202945)

* Mon Aug 21 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-24
- remove copy of xenguest-install from this package, require 
  python-xeninst (the new home of xenguest-install)

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-23
- add patch to fix rtl8139 in FV, switch it back to the default nic
- add necessary ia64 patches (#201040)
- build on ia64

* Fri Jul 28 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-22
- add patch to fix net devices for HVM guests 

* Fri Jul 28 2006 Rik van Riel <riel@redhat.com> - 3.0.2-21
- make sure disk IO from HVM guests actually hits disk (#198851)

* Fri Jul 28 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-20
- don't start blktapctrl for now
- fix HVM guest creation in xenguest-install
- make sure log files have the right SELinux label

* Tue Jul 25 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-19
- fix libblktap symlinks (#199820)
- make libxenstore executable (#197316)
- version libxenstore (markmc) 

* Fri Jul 21 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-18
- include /var/xen/dump in file list
- load blkbk, netbk and netloop when xend starts
- update to cs 10712
- avoid file conflicts with qemu (#199759)

* Wed Jul 19 2006 Mark McLoughlin <markmc@redhat.com> - 3.0.2-17
- libxenstore is unversioned, so make xen-libs own it rather
  than xen-devel

* Wed Jul 19 2006 Mark McLoughlin <markmc@redhat.com> 3.0.2-16
- Fix network-bridge error (#199414)

* Mon Jul 17 2006 Daniel Veillard <veillard@redhat.com> - 3.0.2-15
- desactivating the relocation server in xend conf by default and
  add a warning text about it.

* Thu Jul 13 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-14
- Compile fix: don't #include <linux/compiler.h>

* Thu Jul 13 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-13
- Update to xen-unstable cset 10675
- Remove internal libvncserver build, new qemu device model has its own one
  now.
- Change default FV NIC model from rtl8139 to ne2k_pci until the former works
  better

* Tue Jul 11 2006 Daniel Veillard <veillard@redhat.com> - 3.0.2-12
- bump libvirt requires to 0.1.2
- drop xend httpd localhost server and use the unix socket instead

* Mon Jul 10 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-11
- split into main packages + -libs and -devel subpackages for #198260
- add patch from jfautley to allow specifying other bridge for 
  xenguest-install (#198097)

* Mon Jul  3 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-10
- make xenguest-install work with relative paths to disk 
  images (markmc, #197518)

* Fri Jun 23 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-9
- own /var/run/xend for selinux (#196456, #195952)

* Tue Jun 13 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-8
- fix syntax error in xenguest-install

* Mon Jun 12 2006 Daniel Veillard <veillard@redhat.com> - 3.0.2-7
- more initscript patch to report status #184452

* Wed Jun  7 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-6
- Add BuildRequires: for gnu/stubs-32.h so that x86_64 builds pick up
  glibc32 correctly

* Wed Jun  7 2006 Stephen C. Tweedie <sct@redhat.com> - 3.0.2-5
- Rebase to xen-unstable cset 10278

* Fri May  5 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-4
- update to new snapshot (changeset 9925)

* Thu Apr 27 2006 Daniel Veillard <veillard@redhat.com> - 3.0.2-3
- xen.h now requires xen-compat.h, install it too

* Wed Apr 26 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-2
- -m64 patch isn't needed anymore either

* Tue Apr 25 2006 Jeremy Katz <katzj@redhat.com> - 3.0.2-1
- update to post 3.0.2 snapshot (changeset:   9744:1ad06bd6832d)
- stop applying patches that are upstreamed
- add patches for bootloader to run on all domain creations
- make xenguest-install create a persistent uuid
- use libvirt for domain creation in xenguest-install, slightly improve 
  error handling

* Tue Apr 18 2006 Daniel Veillard <veillard@redhat.com> - 3.0.1-5
- augment the close on exec patch with the fix for #188361

* Thu Mar  9 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-4
- add udev rule so that /dev/xen/evtchn gets created properly
- make pygrub not use /tmp for SELinux
- make xenguest-install actually unmount its nfs share.  also, don't use /tmp

* Tue Mar  7 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-3
- set /proc/xen/privcmd and /var/log/xend-debug.log as close on exec to avoid
  SELinux problems
- give better feedback on invalid urls (#184176)

* Mon Mar  6 2006 Stephen Tweedie <sct@redhat.com> - 3.0.1-2
- Use kva mmap to find the xenstore page (upstream xen-unstable cset 9130)

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-1
- fix xenguest-install so that it uses phy: for block devices instead of 
  forcing them over loopback.  
- change package versioning to be a little more accurate

* Thu Mar  2 2006 Stephen Tweedie <sct@redhat.com> - 3.0.1-0.20060301.fc5.3
- Remove unneeded CFLAGS spec file hack

* Thu Mar  2 2006 Rik van Riel <riel@redhat.com> - 3.0.1-0.20060301.fc5.2
- fix 64 bit CFLAGS issue with vmxloader and hvmloader

* Wed Mar  1 2006 Stephen Tweedie <sct@redhat.com> - 3.0.1-0.20060301.fc5.1
- Update to xen-unstable cset 9022

* Tue Feb 28 2006 Stephen Tweedie <sct@redhat.com> - 3.0.1-0.20060228.fc5.1
- Update to xen-unstable cset 9015

* Thu Feb 23 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-0.20060208.fc5.3
- add patch to ensure we get a unique fifo for boot loader (#182328)
- don't try to read the whole disk if we can't find a partition table 
  with pygrub 
- fix restarting of domains (#179677)

* Thu Feb  9 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-0.20060208.fc5.2
- fix -h conflict for xenguest-isntall

* Wed Feb  8 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-0.20060208.fc5.1
- turn on http listener so you can do things with libvir as a user

* Wed Feb  8 2006 Jeremy Katz <katzj@redhat.com> - 3.0.1-0.20060208.fc5
- update to current hg snapshot for HVM support
- update xenguest-install for hvm changes.  allow hvm on svm hardware
- fix a few little xenguest-install bugs

* Tue Feb  7 2006 Jeremy Katz <katzj@redhat.com> - 3.0-0.20060130.fc5.6
- add a hack to fix VMX guests with video to balloon enough (#180375)

* Tue Feb  7 2006 Jeremy Katz <katzj@redhat.com> - 3.0-0.20060130.fc5.5
- fix build for new udev

* Tue Feb  7 2006 Jeremy Katz <katzj@redhat.com> - 3.0-0.20060130.fc5.4
- patch from David Lutterkort to pass macaddr (-m) to xenguest-install
- rework xenguest-install a bit so that it can be used for creating 
  fully-virtualized guests as well as paravirt.  Run with --help for 
  more details (or follow the prompts)
- add more docs (noticed by Andrew Puch)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 3.0-0.20060130.fc5.3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Feb  2 2006 Bill Nottingham <notting@redhat.com> 3.0-0.20060130.fc5.3
- disable iptables/ip6tables/arptables on bridging when bringing up a
  Xen bridge. If complicated filtering is needed that uses this, custom
  firewalls will be needed. (#177794)

* Tue Jan 31 2006 Bill Nottingham <notting@redhat.com> 3.0-0.20060130.fc5.2
- use the default network device, don't hardcode eth0

* Tue Jan 31 2006  <sct@redhat.com> - 3.0-0.20060130.fc5.1
- Add xenguest-install.py in /usr/sbin

* Mon Jan 30 2006  <sct@redhat.com> - 3.0-0.20060130.fc5
- Update to xen-unstable from 20060130 (cset 8705)

* Wed Jan 25 2006 Jeremy Katz <katzj@redhat.com> - 3.0-0.20060110.fc5.5
- buildrequire dev86 so that vmx firmware gets built
- include a copy of libvncserver and build vmx device models against it 

* Tue Jan 24 2006 Bill Nottingham <notting@redhat.com> - 3.0-0.20060110.fc5.4
- only put the udev rules in one place

* Fri Jan 20 2006 Jeremy Katz <katzj@redhat.com> - 3.0-0.20060110.fc5.3
- move xsls to xenstore-ls to not conflict (#171863)

* Tue Jan 10 2006  <sct@redhat.com> - 3.0-0.20060110.fc5.1
- Update to xen-unstable from 20060110 (cset 8526)

* Thu Dec 22 2005 Jesse Keating <jkeating@redhat.com> - 3.0-0.20051206.fc5.2
- rebuilt

* Tue Dec  6 2005 Juan Quintela <quintela@trasno.org> - 3.0-0.20051206.fc5.1
- 20051206 version (should be 3.0.0).
- Remove xen-bootloader fixes (integrated upstream).

* Wed Nov 30 2005 Daniel Veillard <veillard@redhat.com> - 3.0-0.20051109.fc5.4
- adding missing headers for libxenctrl and libxenstore
- use libX11-devel build require instead of xorg-x11-devel

* Mon Nov 14 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051109.fc5.3
- change default dom0 min-mem to 256M so that dom0 will try to balloon down

* Sat Nov 12 2005 Jeremy Katz <katzj@redhat.com>
- buildrequire ncurses-devel (reported by Justin Dearing)

* Thu Nov 10 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051109.fc5.2
- actually enable the initscripts

* Wed Nov  9 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051109.fc5.1
- udev rules moved

* Wed Nov  9 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051109.fc5
- update to current -unstable
- add patches to fix pygrub 

* Wed Nov  9 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051108.fc5
- update to current -unstable

* Fri Oct 21 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20051021.fc5
- update to current -unstable

* Thu Sep 15 2005 Jeremy Katz <katzj@redhat.com> - 3.0-0.20050912.fc5.1
- doesn't require twisted anymore

* Mon Sep 12 2005 Rik van Riel <riel@redhat.com> 3.0-0.20050912.fc5
- add /var/{lib,run}/xenstored to the %files section (#167496, #167121)
- upgrade to today's Xen snapshot
- some small build fixes for x86_64
- enable x86_64 builds

* Thu Sep  8 2005 Rik van Riel <riel@redhat.com> 3.0-0.20050908
- explicitly call /usr/sbin/xend from initscript (#167407)
- add xenstored directories to spec file (#167496, #167121)
- misc gcc4 fixes 
- spec file cleanups (#161191)
- upgrade to today's Xen snapshot
- change the version to 3.0-0.<date> (real 3.0 release will be 3.0-1)

* Mon Aug 23 2005 Rik van Riel <riel@redhat.com> 2-20050823
- upgrade to today's Xen snapshot

* Mon Aug 15 2005 Rik van Riel <riel@redhat.com> 2-20050726
- upgrade to a known-working newer Xen, now that execshield works again

* Mon May 30 2005 Rik van Riel <riel@redhat.com> 2-20050530
- create /var/lib/xen/xen-db/migrate directory so "xm save" works (#158895)

* Mon May 23 2005 Rik van Riel <riel@redhat.com> 2-20050522
- change default display method for VMX domains to SDL

* Fri May 20 2005 Rik van Riel <riel@redhat.com> 2-20050520
- qemu device model for VMX

* Thu May 19 2005 Rik van Riel <riel@redhat.com> 2-20050519
- apply some VMX related bugfixes

* Mon Apr 25 2005 Rik van Riel <riel@redhat.com> 2-20050424
- upgrade to last night's snapshot

* Fri Apr 15 2005 Jeremy Katz <katzj@redhat.com>
- patch manpath instead of moving in specfile.  patch sent upstream
- install to native python path instead of /usr/lib/python
- other misc specfile duplication cleanup

* Sun Apr  3 2005 Rik van Riel <riel@redhat.com> 2-20050403
- fix context switch between vcpus in same domain, vcpus > cpus works again

* Sat Apr  2 2005 Rik van Riel <riel@redhat.com> 2-20050402
- move initscripts to /etc/rc.d/init.d (Florian La Roche) (#153188)
- ship only PDF documentation, not the PS or tex duplicates

* Thu Mar 31 2005 Rik van Riel <riel@redhat.com> 2-20050331
- upgrade to new xen hypervisor
- minor gcc4 compile fix

* Mon Mar 28 2005 Rik van Riel <riel@redhat.com> 2-20050328
- do not yet upgrade to new hypervisor ;)
- add barrier to fix SMP boot bug
- add tags target
- add zlib-devel build requires (#150952)

* Wed Mar  9 2005 Rik van Riel <riel@redhat.com> 2-20050308
- upgrade to last night's snapshot
- new compile fix patch

* Sun Mar  6 2005 Rik van Riel <riel@redhat.com> 2-20050305
- the gcc4 compile patches are now upstream
- upgrade to last night's snapshot, drop patches locally

* Fri Mar  4 2005 Rik van Riel <riel@redhat.com> 2-20050303
- finally got everything to compile with gcc4 -Wall -Werror

* Thu Mar  3 2005 Rik van Riel <riel@redhat.com> 2-20050303
- upgrade to last night's Xen-unstable snapshot
- drop printf warnings patch, which is upstream now

* Wed Feb 23 2005 Rik van Riel <riel@redhat.com> 2-20050222
- upgraded to last night's Xen snapshot
- compile warning fixes are now upstream, drop patch

* Sat Feb 19 2005 Rik van Riel <riel@redhat.com> 2-20050219
- fix more compile warnings
- fix the fwrite return check

* Fri Feb 18 2005 Rik van Riel <riel@redhat.com> 2-20050218
- upgrade to last night's Xen snapshot
- a kernel upgrade is needed to run this Xen, the hypervisor
  interface changed slightly
- comment out unused debugging function in plan9 domain builder
  that was giving compile errors with -Werror

* Tue Feb  8 2005 Rik van Riel <riel@redhat.com> 2-20050207
- upgrade to last night's Xen snapshot

* Tue Feb  1 2005 Rik van Riel <riel@redhat.com> 2-20050201.1
- move everything to /var/lib/xen

* Tue Feb  1 2005 Rik van Riel <riel@redhat.com> 2-20050201
- upgrade to new upstream Xen snapshot

* Tue Jan 25 2005 Jeremy Katz <katzj@redhat.com>
- add buildreqs on python-devel and xorg-x11-devel (strange AT nsk.no-ip.org)

* Mon Jan 24 2005 Rik van Riel <riel@redhat.com> - 2-20050124
- fix /etc/xen/scripts/network to not break with ipv6 (also sent upstream)

* Fri Jan 14 2005 Jeremy Katz <katzj@redhat.com> - 2-20050114
- update to new snap
- python-twisted is its own package now
- files are in /usr/lib/python now as well, ugh.

* Tue Jan 11 2005 Rik van Riel <riel@redhat.com>
- add segment fixup patch from xen tree
- fix %files list for python-twisted

* Mon Jan 10 2005 Rik van Riel <riel@redhat.com>
- grab newer snapshot, that does start up
- add /var/xen/xend-db/{domain,vnet} to %files section

* Thu Jan  6 2005 Rik van Riel <riel@redhat.com>
- upgrade to new snapshot of xen-unstable

* Mon Dec 13 2004 Rik van Riel <riel@redhat.com>
- build python-twisted as a subpackage
- update to latest upstream Xen snapshot

* Sun Dec  5 2004 Rik van Riel <riel@redhat.com>
- grab new Xen tarball (with wednesday's patch already included)
- transfig is a buildrequire, add it to the spec file

* Wed Dec  1 2004 Rik van Riel <riel@redhat.com>
- fix up Che's spec file a little bit
- create patch to build just Xen, not the kernels

* Wed Dec 01 2004 Che
- initial rpm release
