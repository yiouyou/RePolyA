#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 14:43
@Author  : alexanderwu
@File    : __init__.py
"""

from repolya.metagpt.roles.role import Role
from repolya.metagpt.roles.architect import Architect
from repolya.metagpt.roles.project_manager import ProjectManager
from repolya.metagpt.roles.product_manager import ProductManager
from repolya.metagpt.roles.engineer import Engineer
from repolya.metagpt.roles.qa_engineer import QaEngineer
from repolya.metagpt.roles.seacher import Searcher
from repolya.metagpt.roles.sales import Sales
from repolya.metagpt.roles.customer_service import CustomerService


__all__ = [
    "Role",
    "Architect",
    "ProjectManager",
    "ProductManager",
    "Engineer",
    "QaEngineer",
    "Searcher",
    "Sales",
    "CustomerService",
]
