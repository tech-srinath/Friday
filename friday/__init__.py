# -*- coding: utf-8 -*-
from __future__ import absolute_import
from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]

__author__ = """Isaac Luke Smith"""
__email__ = 'sentherus@gmail.com'
__version__ = '0.3.4'
