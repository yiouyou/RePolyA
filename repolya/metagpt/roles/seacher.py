#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/23 17:25
@Author  : alexanderwu
@File    : seacher.py
"""
from repolya.metagpt.actions import ActionOutput, SearchAndSummarize
from repolya._log import logger_metagpt
from repolya.metagpt.roles import Role
from repolya.metagpt.schema import Message
from repolya.metagpt.tools import SearchEngineType


class Searcher(Role):
    def __init__(self, name='Alice', profile='Smart Assistant', goal='Provide search services for users',
                 constraints='Answer is rich and complete', engine=SearchEngineType.SERPAPI_GOOGLE, **kwargs):
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([SearchAndSummarize(engine=engine)])

    def set_search_func(self, search_func):
        action = SearchAndSummarize("", engine=SearchEngineType.CUSTOM_ENGINE, search_func=search_func)
        self._init_actions([action])

    async def _act_sp(self) -> Message:
        logger_metagpt.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(self._rc.memory.get(k=0))
        # logger_metagpt.info(response)
        if isinstance(response, ActionOutput):
            msg = Message(content=response.content, instruct_content=response.instruct_content,
                            role=self.profile, cause_by=type(self._rc.todo))
        else:
            msg = Message(content=response, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)

    async def _act(self) -> Message:
        return await self._act_sp()
