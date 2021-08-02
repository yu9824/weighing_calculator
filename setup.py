"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup, find_packages
from shutil import copyfile
import os
import sys

# 再帰回数に引っかかるのでとりあえず大きい数に．
sys.setrecursionlimit(10 ** 9)


# ------------------------ ここを変更 --------------------------------
VERSION = '0.5.0'
VERSION_PYTHON = '{0}.{1}'.format(sys.version_info.major, sys.version_info.minor)
APP_NAME = 'weighing_calculator'
DESCRIPTION = 'Calculate weghing.'
AUTHOR = 'yu9824'
ID = 'yu9824'
EMAIL = '{0}@{1}'.format('yu.9824.job', 'gmail.com')

# py2app用の変数
SRC = ['main.py']
DATA_FILES = ['settings.json', 'LICENSE', 'about.txt']
# PKGS = ['pandas', 'numpy', 'xlwt', 'element_recognition', 'PySimpleGUI', 'pymatgen', 'openpyxl']
PKGS = ['pandas', 'numpy', 'element_recognition', 'PySimpleGUI', 'pymatgen', 'openpyxl']
ICON = os.path.join('icon', '{}.icns'.format(APP_NAME))
# --------------------------------------------------------------------

'''
メモ
/.pyenv/versions/anaconda3-2019.03/envs/pymat/lib/python3.7/site-packages/PyQt5/uic/port_v2/ascii_upper.pyの28行目を書き換えた．
少なくともpython3.7においてstringオブジェクトはmaketrans関数を持っておらず，正しくはstr.maketransである．
python3.8で以前やったときはこのエラーがでなかった．
* 3.8にアップデートしてやってみる．
    → 3.8だとsetupのほうがエラー起きるので3.6でやってみる．
    3.6は起動後に関数が呼び出せないと言われる
    python3.9.6では動いた！！

setup.pyに関する参考サイト
* https://packaging.python.org/guides/distributing-packages-using-setuptools/#packages

py2app 0.23や0.22では動作確認
'''

if 'py2app' in sys.argv:
    alias = '-A' in sys.argv or '--alias' in sys.argv

    # 諸変数・定数の定義
    lib_path = os.path.join(os.environ['CONDA_PREFIX'], 'lib')
    fname_libpython = 'libpython{}.dylib'.format(VERSION_PYTHON)

    # libpython3.7.m.dylibだとエラーになるのであらかじめコピーしておく．
    path_original = os.path.join(lib_path, 'libpython{}m.dylib'.format(VERSION_PYTHON))
    path_converted = os.path.join(lib_path, fname_libpython)
    if os.path.exists(path_original) and not os.path.exists(path_converted):
        copyfile(path_original, path_converted)

    # 諸変数の準備
    dylib_files = [os.path.join(lib_path, f) for f in os.listdir(lib_path) if '.dylib' in f]
    contents_path = os.path.join('dist', '{}.app'.format(APP_NAME), 'Contents')
    frameworks_path = os.path.join(contents_path, 'Frameworks')

    OPTIONS = {
        'argv_emulation': False,
        'packages': PKGS,
        'iconfile': ICON,
        'plist':{
            'PyRuntimeLocations':[
                '@executable_path/../Frameworks/{}'.format(fname_libpython),
                os.path.join(lib_path, fname_libpython),
            ],
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleGetInfoString': DESCRIPTION,
            'CFBundleIdentifier': "com.{0}.osx.{1}".format(ID, APP_NAME),
            'CFBundleVersion': VERSION,
            'CFBundleShortVersionString': VERSION,
            'NSHumanReadableCopyright': u"Copyright © 2020-, {}".format(AUTHOR)
        },
        # 'frameworks': dylib_files,
    }

    setup(
        name = APP_NAME,
        app = SRC,
        author = AUTHOR,
        author_email = EMAIL,
        version = VERSION,
        data_files = DATA_FILES,
        options = {'py2app': OPTIONS},
        setup_requires = ['py2app'],
        url = 'https://github.com/{0}/{1}'.format(ID, APP_NAME),
    )

    # aliasモードじゃないとき．
    # if not alias:
    #     {copyfile(f, os.path.join(frameworks_path, os.path.basename(f))) for f in dylib_files}
else:
    with open('requirements.txt') as requirements_file:
        install_requirements = requirements_file.read().splitlines()

    setup(
        name = APP_NAME,
        version = VERSION,
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = EMAIL,
        install_requires = install_requirements,
        url = 'https://github.com/{0}/{1}'.format(ID, APP_NAME),
        # license = license,
        packages = find_packages(exclude=['example'])
    )
