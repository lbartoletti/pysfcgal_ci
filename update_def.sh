#!/usr/bin/env sh

if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then
  echo "Usage: $0 sfcgal_c.h " >&2
  exit 1
fi

# sfcgal_def.c
sed -e '4,/endif/d;/__cplusplus/,$d' -e "s/SFCGAL_API //" -e "/^#if/d" -e "/^#endif/d" ${1} > pysfcgal/sfcgal_def.c
printf "void\nfree(void*);" >> pysfcgal/sfcgal_def.c
echo "pysfcgal/sfcgal_def.c has been updated!"

# sfcgal_def_msvc.c
sed -e '4,/endif/d;/__cplusplus/,$d' -e "s/SFCGAL_API //" -e "/^#if/d" -e "/^#endif/d" ${1} > pysfcgal/sfcgal_def_msvc.c
# remove the Alpha shapes entries from the C API for the MSVC compiler
# found in https://stackoverflow.com/questions/876446/how-do-i-delete-a-matching-line-the-line-above-and-the-one-below-it-using-sed
ed -s pysfcgal/sfcgal_def_msvc.c <<< '/^sfcgal_geometry_alpha_shapes.*/ -1, /^sfcgal_geometry_alpha_shapes.*/ +1 d'$'\n'w
ed -s pysfcgal/sfcgal_def_msvc.c <<< '/^sfcgal_geometry_optimal_alpha_shapes.*/ -1, /^sfcgal_geometry_optimal_alpha_shapes.*/ +1 d'$'\n'w
printf "void\nfree(void*);" >> pysfcgal/sfcgal_def_msvc.c
echo "pysfcgal/sfcgal_def_msvc.c has been updated!"
