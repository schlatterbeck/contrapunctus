# Copyright (C) 2017-2022 Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# ****************************************************************************
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
# ****************************************************************************

import pytest
from pga.testsupport import pga_setup_test, pytest_runtest_makereport

def pytest_addoption (parser):
    parser.addoption \
        ( '--longrun'
        , action = 'store_true'
        , help   = "enable @pytest.mark.slow decorated tests"
        )
# end def pytest_addoption

def pytest_configure (config):
    config.addinivalue_line ("markers", "slow: mark test as slow to run")
# end def pytest_configure

def pytest_collection_modifyitems (config, items):
    if config.getoption ("--longrun"):
        # with --longrun option: do not skip slow tests
        return
    skip_slow = pytest.mark.skip (reason = "Skipping long-running tests")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker (skip_slow)
# end def pytest_collection_modifyitems
