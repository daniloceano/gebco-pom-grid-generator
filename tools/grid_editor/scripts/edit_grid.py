#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Wrapper para Grid Editor
================================

Facilita o uso do editor de grades.
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grid_editor import main

if __name__ == '__main__':
    sys.exit(main())
