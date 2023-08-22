#!/usr/bin/env python
# -*- coding: utf-8 -*-

from metagpt.actions import BossRequirement, WritePRD
from metagpt.roles import Role


class ProductManager(Role):
    def __init__(
        self,
        name="Product Manager",
        profile="Product Manager",
        goal="Efficiently create a successful product",
        constraints=""
    ):
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WritePRD])
        self._watch([BossRequirement])
