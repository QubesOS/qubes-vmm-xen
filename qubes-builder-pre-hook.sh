#!/bin/sh

# DIST_SRC_ROOT and DIST_SRC are provided by qubes-builder

[ -z "$DIST_SRC" ] && exit 1

# Copy components required for stubdom
rm -rf $DIST_SRC/{gui,vchan}
cp -al $PWD/qubes-src/gui-agent-xen-hvm-stubdom $DIST_SRC/gui
cp -al $PWD/qubes-src/gui-common/include/qubes-gui*.h $DIST_SRC/gui/include/
cp -al $PWD/qubes-src/core-vchan-xen/vchan $DIST_SRC/vchan
rm -rf $DIST_SRC/*/rpm/{x86_64,i686,noarch}
