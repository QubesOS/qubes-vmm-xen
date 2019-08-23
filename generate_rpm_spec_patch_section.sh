#!/bin/bash
patches=$(cat series-fedora.conf series-common.conf | grep -nv "^#\|^$" | sed -E 's/^([0-9]+):(.*)$/Patch\1: \2/')
xenspecin=$(grep -Ev "^Patch[0-9]+:" xen.spec.in | awk -v r="$patches" '1;/#INSERT_PATCH/{print r}')
echo "$xenspecin" > xen.spec.in
