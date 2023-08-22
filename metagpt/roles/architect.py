#!/usr/bin/env python
# -*- coding: utf-8 -*-

from metagpt.actions import WriteDesign, WritePRD
from metagpt.roles import Role


class Architect(Role):
    """Architect: Listen to PRD, responsible for designing API, designing code files"""
    def __init__(
        self,
        name="Architect",
        profile="Architect",
        goal="Design a concise, usable, complete python system",
        constraints="Try to specify good open source tools as much as possible")
    :
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteDesign])
        self._watch({WritePRD})
