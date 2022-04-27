#!/usr/bin/env sh

if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then
  echo "Usage: $0 sfcgal_c.h " >&2
  exit 1
fi

sed -e '4,/endif/d;/__cplusplus/,$d' -e "s/SFCGAL_API //" ${1} > pysfcgal/sfcgal_def.c
printf "void\nfree(void*);" >> pysfcgal/sfcgal_def.c

