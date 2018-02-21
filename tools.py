#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2018 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import glob
import shlex
import subprocess
import shutil


def ejecuta(comando):
    print('Ejecutando... %s' % comando)
    args = shlex.split(comando)
    p = subprocess.Popen(args, bufsize=10000, stdout=subprocess.PIPE)
    valor = p.communicate()[0]
    return valor


def list_src():
    file_txt = os.path.join(MAIN_DIR, 'files.txt')
    f = open(file_txt, 'w')
    for file in glob.glob(os.path.join(SRC_DIR, '**', '*.py'), recursive=True):
        print(file)
        f.write('%s\n' % file)
    f.close()
    return file_txt


def list_languages():
    lans = []
    file_txt = os.path.join(LANGUAGES_DIR, 'languages.txt')
    if os.path.exists(file_txt) is True:
        f = open(file_txt, 'r')
        for linea in f.readlines():
            lan = linea[:-1]
            print(lan)
            lans.append(lan)
        f.close()
    for file in glob.glob(os.path.join(LANGUAGES_DIR, '*.po')):
        lan = os.path.splitext(os.path.basename(file))[0]
        if lan not in lans:
            lans.append(lan)
    f = open(file_txt, 'w')
    for lan in lans:
        f.write('%s\n' % lan)
    f.close()
    return file_txt


def update_translations():
    file_txt = os.path.join(LANGUAGES_DIR, 'languages.txt')
    f = open(file_txt, 'r')
    for file in f.readlines():
        lan = file[:-1]
        file = os.path.join(LANGUAGES_DIR, lan + '.po')
        print('############################################################')
        print(lan)
        print('############################################################')
        if os.path.exists(file):
            command = 'msgmerge -U %s %s' % (file, TEMPLATE)
        else:
            command = 'msginit --output-file=%s --input=%s --locale=%s' % (
                file, TEMPLATE, lan)
        print(ejecuta(command))
        edit_language_file(file)
    f.close()


def edit_language_file(file):
    fr = open(file, 'r')
    file_out = file + '.new'
    fs = open(file_out, 'w')
    for line in fr.readlines():
        if line.find('Project-Id-Version:') != -1:
            line = '"Project-Id-Version: %s %s\\n"\n' % (APP, VERSION)
        elif line.find('Content-Type:') != -1:
            line = '"Content-Type: text/plain; charset=UTF-8\\n"\n'
        fs.write(line)
    fs.close()
    fr.close()
    shutil.move(file_out, file)


def remove_security_copies():
    for file in glob.glob(os.path.join(LANGUAGES_DIR, '*.po~')):
        os.remove(file)


def get_files_in_folder(folder):
    files = []
    for file in glob.glob(os.path.join(folder, '*')):
        if file is not None and os.path.exists(file):
            if os.path.isdir(file):
                files.extend(get_files_in_folder(file))
            else:
                files.append(file)
    return files


def remove_files(dir, ext):
    for file in get_files_in_folder(dir):
        if os.path.splitext(file)[1] == ext:
            os.remove(file)


def remove_compiled_files(dir):
    remove_files(dir, '.pyc')


def remove_languages_saved_files(dir):
    remove_files(dir, '.po~')


def create_temporal_file(dir):
    temp_file = os.path.join(MAIN_DIR, 'temp_files.txt')
    f = open(temp_file, 'w')
    for file in get_files_in_folder(dir):
        f.write('%s\n' % file)
    f.close()
    return temp_file


def create_rules(file):
    if os.path.exists(file):
        os.remove(file)
    f = open(file, 'w')
    f.write('#!/usr/bin/make -f\n')
    f.write('# Sample debian/rules that uses debhelper.\n')
    f.write('# This file is public domain software, originally written by\
 Joey Hess.\n')
    f.write('#\n')
    f.write('# This version is for packages that are architecture\
 independent.\n')
    f.write('\n')
    f.write('# Uncomment this to turn on verbose mode.\n')
    f.write('#export DH_VERBOSE=1\n')
    f.write('\n')
    f.write('build: build-stamp\n')
    f.write('build-stamp:\n')
    f.write('\tdh_testdir\n')
    f.write('\n')
    f.write('\t# Add here commands to compile the package.\n')
    f.write('\t#$(MAKE)\n')
    f.write('\n')
    f.write('\ttouch build-stamp\n')
    f.write('\n')
    f.write('clean:\n')
    f.write('\tdh_testdir\n')
    f.write('\tdh_testroot\n')
    f.write('\trm -f build-stamp\n')
    f.write('\n')
    f.write('\t# Add here commands to clean up after the build process.\n')
    f.write('\t#$(MAKE) clean\n')
    f.write('\t#$(MAKE) distclean\n')
    f.write('\n')
    f.write('\tdh_clean\n')
    f.write('\n')
    f.write('install: build\n')
    f.write('\tdh_testdir\n')
    f.write('\tdh_testroot\n')
    f.write('\tdh_prep\n')
    f.write('\tdh_installdirs\n')
    f.write('\tdh_install\n')

    f.write('\t# Create languages directories\n')
    file_txt = os.path.join(LANGUAGES_DIR, 'languages.txt')
    fl = open(file_txt, 'r')
    for lan in fl.readlines():
        lan = lan[:-1]
        f.write('\tmkdir -p ${CURDIR}/debian/%s/usr/share/\
locale-langpack/%s/LC_MESSAGES\n' % (APP, lan))
    fl.close()
    f.write('\t# End create languages directories\n')

    f.write('\t# Compile languages\n')
    file_txt = os.path.join(LANGUAGES_DIR, 'languages.txt')
    fl = open(file_txt, 'r')
    for lan in fl.readlines():
        lan = lan[:-1]
        f.write('\tmsgfmt po/%s.po -o ${CURDIR}/debian/%s/usr/share/\
locale-langpack/%s/LC_MESSAGES/%s.mo\n' % (lan, APP, lan, APP))
    fl.close()
    f.write('\t# End comile languages\n')
    ####################################################################
    f.write('\n')
    f.write('\t# Add here commands to install the package into debian/\
<packagename>.\n')
    f.write('\t#$(MAKE) prefix=`pwd`/debian/`dh_listpackages`/usr install\n')
    f.write('\n')
    f.write('# Build architecture-independent files here.\n')
    f.write('binary-indep: build install\n')
    f.write('\tdh_testdir\n')
    f.write('\tdh_testroot\n')
    f.write('\tdh_installchangelogs\n')
    f.write('\tdh_installdocs\n')
    f.write('\tdh_installexamples\n')
    f.write('\t# added gconf and icons\n')
    f.write('\tdh_gconf\n')
    f.write('\tdh_icons\n')
    f.write('#\tdh_installmenu\n')
    f.write('#\tdh_installdebconf\n')
    f.write('#\tdh_installlogrotate\n')
    f.write('#\tdh_installemacsen\n')
    f.write('#\tdh_installcatalogs\n')
    f.write('#\tdh_installpam\n')
    f.write('#\tdh_installmime\n')
    f.write('#\tdh_installinit\n')
    f.write('#\tdh_installcron\n')
    f.write('#\tdh_installinfo\n')
    f.write('#\tdh_installwm\n')
    f.write('#\tdh_installudev\n')
    f.write('#\tdh_lintian\n')
    f.write('#\tdh_bugfiles\n')
    f.write('#\tdh_undocumented\n')
    f.write('\tdh_installman\n')
    f.write('\tdh_link\n')
    f.write('\tdh_compress\n')
    f.write('\tdh_fixperms\n')
    f.write('#\tdh_perl\n')
    f.write('#\tdh_pysupport\n')
    f.write('\tdh_installdeb\n')
    f.write('\tdh_gencontrol\n')
    f.write('\tdh_md5sums\n')
    f.write('\tdh_builddeb\n')
    f.write('\n')
    f.write('# Build architecture-dependent files here.\n')
    f.write('binary-arch: build install\n')
    f.write('# We have nothing to do by default.\n')
    f.write('\n')
    f.write('binary: binary-indep binary-arch\n')
    f.write('.PHONY: build clean binary-indep binary-arch binary install\n')
    f.close()
    os.chmod(file, 777)


def delete_it(file):
    if os.path.exists(file):
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)


def babilon():
    print('############################################################')
    print('Parent dir -> %s' % MAIN_DIR)
    print('Languages dir -> %s' % LANGUAGES_DIR)
    print('Source dir -> %s' % SRC_DIR)
    print('############################################################')
    print('Updating template')
    print('############################################################')
    files_file = list_src()
    print(files_file)
    command = 'xgettext --msgid-bugs-address=%s --language=Python --keyword=\
_ --keyword=N_ --output=%s --files-from=%s' % (AUTHOR_EMAIL,
                                               TEMPLATE,
                                               files_file)
    print(ejecuta(command))
    delete_it(files_file)
    print('############################################################')
    print('List languages')
    print('############################################################')
    #
    list_languages()
    #
    print('############################################################')
    print('Updating translations')
    print('############################################################')
    update_translations()
    print('############################################################')
    print('Removing security copies')
    print('############################################################')
    remove_security_copies()


if __name__ == '__main__':
    MAIN_DIR = os.getcwd()
    DEBIAN_DIR = os.path.join(MAIN_DIR, 'debian')
    LANGUAGES_DIR = os.path.join(MAIN_DIR, 'po')
    SRC_DIR = os.path.join(MAIN_DIR, 'src')
    TEMPLATE = os.path.join(LANGUAGES_DIR, 'po.pot')
    CHANGELOG = os.path.join(DEBIAN_DIR, 'changelog')
    if os.path.exists(CHANGELOG):
        f = open(CHANGELOG, 'r')
        line = f.readline()
        print(line)
        f.close()
        pos = line.find('(')
        posf = line.find('-', pos)
        APP = line[:pos].strip()
        VERSION = line[pos + 1: posf].strip()
        APPNAME = APP.title()
        AUTHOR = 'Lorenzo Carbonell'
        AUTHOR_EMAIL = 'lorenzo.carbonell.cerezo@gmail.com'
        babilon()
        rules_file = os.path.join(DEBIAN_DIR, 'rules')
        if os.path.exists(rules_file):
            delete_it(rules_file)
            create_rules(rules_file)
            print(rules_file)
    exit(0)
