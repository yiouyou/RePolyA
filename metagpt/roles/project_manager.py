#!/usr/bin/env python
# -*- coding: utf-8 -*-

from metagpt.actions import WriteDesign, WriteTasks
from metagpt.roles import Role


class ProjectManager(Role):
    def __init__(
        self,
        name="Project Manager",
        profile="Project Manager",
        goal="Improve team efficiency and deliver with quality and quantity",
        constraints=""
    ):
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteTasks])
        self._watch([WriteDesign])
