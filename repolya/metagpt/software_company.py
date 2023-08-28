#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/12 00:30
@Author  : alexanderwu
@File    : software_company.py
"""
from pydantic import BaseModel, Field

from repolya.metagpt.actions import BossRequirement
from repolya.metagpt.config import CONFIG
from repolya.metagpt.environment import Environment
from repolya._log import logger_metagpt
from repolya.metagpt.roles import Role
from repolya.metagpt.schema import Message
from repolya.metagpt.utils.common import NoMoneyException


class SoftwareCompany(BaseModel):
    """
    Software Company: Possesses a team, SOP (Standard Operating Procedures), and a platform for instant messaging,
    dedicated to writing executable code.
    """
    environment: Environment = Field(default_factory=Environment)
    investment: float = Field(default=10.0)
    idea: str = Field(default="")

    class Config:
        arbitrary_types_allowed = True

    def hire(self, roles: list[Role]):
        """Hire roles to cooperate"""
        self.environment.add_roles(roles)

    def invest(self, investment: float):
        """Invest company. raise NoMoneyException when exceed max_budget."""
        self.investment = investment
        CONFIG.max_budget = investment
        logger_metagpt.info(f'Investment: ${investment}.')

    def _check_balance(self):
        if CONFIG.total_cost > CONFIG.max_budget:
            raise NoMoneyException(CONFIG.total_cost, f'Insufficient funds: {CONFIG.max_budget}')

    def start_project(self, idea):
        """Start a project from publishing boss requirement."""
        self.idea = idea
        self.environment.publish_message(Message(role="BOSS", content=idea, cause_by=BossRequirement))

    def _save(self):
        logger_metagpt.info(self.json())

    async def run(self, n_round=3):
        """Run company until target round or no money"""
        while n_round > 0:
            # self._save()
            n_round -= 1
            logger_metagpt.debug(f"{n_round=}")
            self._check_balance()
            await self.environment.run()
        return self.environment.history
