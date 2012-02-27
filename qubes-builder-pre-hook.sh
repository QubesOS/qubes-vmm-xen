#!/bin/sh

# DIST_SRC_ROOT and DIST_SRC are provided by qubes-builder

# Copy components required for stubdom
for comp in gui core; do
    cp -alt $DIST_SRC_ROOT/$COMPONENT $PWD/qubes-src/$comp
done
rm -rf $DIST_SRC/*/rpm/{x86_64,i686,noarch}
