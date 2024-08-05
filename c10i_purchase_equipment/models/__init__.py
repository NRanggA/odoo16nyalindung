# -*- coding: utf-8 -*-

from . import purchase
from . import product
from . import maintenance
from . import equipment_register


# Purchase Order > Create Inventory Receipt
# Inventory Receipt > Create Equipment Receipt
# Equipment Register > Create Equipment
# ======================================== Part 1
# [DONE] Asset Allocation > Update Equipment Owner
# [DONE] Asset Allocation > Return Equipment
# ======================================== Part 2
# Equipment Receipt > Create Asset Addition
# Asset Addition > Create Accounting Asset
# ======================================== Part 3
# Material Request > Create Issue Product
# Material Request > Asset Allocation

