#!/bin/bash
NEWLINE=$'\n'
TAB=$'\t'
strindex() { 
	x="${1%%$2*}"
	[[ "$x" = "$1" ]] && echo -1 || echo "${#x}"
}

line="$(head -1 debian/changelog)"
package_pos_end=`strindex "$line" " "`
version_pos_start=`strindex "$line" "("`+1
version_pos_end=`strindex "$line" ")"`
package="${line:0:$package_pos_end}"
version="${line:version_pos_start:$version_pos_end-$version_pos_start-2}"

echo "========="
echo $package
echo $version
echo "========="

if [ ! -f po/po.pot ];then
	touch po/po.pot
fi
find . -iname "*.py" | xargs xgettext -L Python --from-code=UTF-8 -k_ -kN_ -o po/po.pot
if [ -d locale ];then
	rm -rf locale/
fi
for i in po/*.po;do
	echo "=== $i ==="
	filename=$(basename "$i")
	lang=${filename/.po}
	file_size=`wc -c < $i`
	if [ $file_size -gt 0 ];then
		msgmerge -U $i po/po.pot
	else
		msginit --output-file=$i --input=po/po.pot --locale=$lang
	fi
	sed -i -e 's/charset=ASCII/charset=UTF-8/g' $i
	sed -i -e "s/PACKAGE VERSION/$package - $version/g" $i
	sed -i -e "s/PACKAGE package/$package package/g" $i
	## Translations
	if [ ! -d locale/$lang ];then
		mkdir -p locale/$lang/LC_MESSAGES
	fi
	echo "=== compile $i ==="
	msgfmt $i -o locale/$lang/LC_MESSAGES/$package.mo
	echo "=== end compile $i ==="
done
for i in po/*.po~;do
	if [ -f $i ];then
		rm $i
	fi
done

echo "=== creating rules ==="
file="debian/rules"
echo "$file"

if [ -f $file ];then
	rm $file
fi
(
cat <<'EOF'
#!/usr/bin/make -f
# Sample debian/rules that uses debhelper.
# This file is public domain software, originally written by Joey Hess.
#
# This version is for packages that are architecture independent.

# Uncomment this to turn on verbose mode.
#export DH_VERBOSE=1

build: build-stamp
build-stamp:
	dh_testdir

	# Add here commands to compile the package.
	#$(MAKE)

	touch build-stamp

clean:
	dh_testdir
	dh_testroot
	rm -f build-stamp

	# Add here commands to clean up after the build process.
	#$(MAKE) clean
	#$(MAKE) distclean

	dh_clean

install: build
	dh_testdir
	dh_testroot
	dh_prep
	dh_installdirs
	dh_install
EOF
) > $file

variable1="${TAB}# Create languages directories"
variable2=''
for i in po/*.po
do
	lang=${i//.po}
	lang=${lang//po\/}
	echo $lang
	#echo '	mkdir -p ${CURDIR}/debian/'$package'/usr/share/locale-langpack/'$lang'/LC_MESSAGES' >> $file
	variable1+="${NEWLINE}${TAB}mkdir -p "'${CURDIR}'"/debian/$package/usr/share/locale-langpack/$lang/LC_MESSAGES"
	variable2+="${NEWLINE}${TAB}msgfmt $i -o "'${CURDIR}'"/debian/$package/usr/share/locale-langpack/$lang/LC_MESSAGES/$package.mo"
done
variable1+="${NEWLINE}${TAB}# End create languages directories"
variable1+="${NEWLINE}${TAB}# Compile languages"
variable1+=$variable2
variable1+="${NEWLINE}${TAB}# End comile languages"
echo "${variable1}" >> $file
(
cat <<'EOF'
	# Add here commands to install the package into debian/<packagename>.
	#$(MAKE) prefix=`pwd`/debian/`dh_listpackages`/usr install

# Build architecture-independent files here.
binary-indep: build install
	dh_testdir
	dh_testroot
	dh_installchangelogs
	dh_installdocs
	dh_installexamples
	# added gconf and icons
	dh_gconf
	dh_icons
#	dh_installmenu
#	dh_installdebconf
#	dh_installlogrotate
#	dh_installemacsen
#	dh_installcatalogs
#	dh_installpam
#	dh_installmime
#	dh_installinit
#	dh_installcron
#	dh_installinfo
#	dh_installwm
#	dh_installudev
#	dh_lintian
#	dh_bugfiles
#	dh_undocumented
	dh_installman
	dh_link
	dh_compress
	dh_fixperms
#	dh_perl
#	dh_pysupport
	dh_installdeb
	dh_gencontrol
	dh_md5sums
	dh_builddeb

# Build architecture-dependent files here.
binary-arch: build install
# We have nothing to do by default.

binary: binary-indep binary-arch
.PHONY: build clean binary-indep binary-arch binary install
EOF
) >> $file

chmod 777 $file