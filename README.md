# Qubes Xen

This is the [Qubes OS](https://www.qubes-os.org) packaging of the
[Xen hypervisor](https://xenproject.org/), the bare-metal hypervisor that Qubes
runs on. It builds upstream Xen with a set of Qubes-specific patches and a Qubes
build configuration, and ships the hypervisor and its tools as the packages that
dom0 installs.

The build pulls the upstream Xen release named in the `version` file straight
from the Xen project's git, then applies the numbered patches
in this repo on top. Those patches cover things like stubdomain handling, PCI
passthrough, EFI boot, and extra hardening; the `config` file holds the Qubes
hypervisor build options.

For how Xen itself works, see the [upstream Xen documentation](https://xenbits.xenproject.org/docs/).
For how Qubes uses it, see the [Qubes OS documentation](https://www.qubes-os.org/doc/).
