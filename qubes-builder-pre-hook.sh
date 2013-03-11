#!/bin/sh

# DIST_SRC_ROOT and DIST_SRC are provided by qubes-builder

# Copy components required for stubdom
cp -alt $DIST_SRC/ $PWD/qubes-src/gui
cp -alt $DIST_SRC/ $PWD/qubes-src/libvchan/vchan
rm -rf $DIST_SRC/*/rpm/{x86_64,i686,noarch}
