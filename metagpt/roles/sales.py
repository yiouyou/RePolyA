#!/usr/bin/env python
# -*- coding: utf-8 -*-

from metagpt.actions import SearchAndSummarize
from metagpt.roles import Role
from metagpt.tools import SearchEngineType


DESC = """
I am a sales guide in retail. My name is Sales. I will answer some customer questions next, and I will answer questions only based on the information in the knowledge base. If I feel that you can't get the answer from the reference material, then I will directly reply that I don't know, and I won't tell you that this is from the knowledge base, but pretend to be what I know. Note that each of my replies will be replied in the tone of a professional guide.
"""

class Sales(Role):
    def __init__(
        self,
        name="Sales",
        profile="Retail sales guide",
        desc=DESC,
        store=None
    ):
        super().__init__(name, profile, desc=desc)
        self._set_store(store)

    def _set_store(self, store):
        if store:
            action = SearchAndSummarize("", engine=SearchEngineType.CUSTOM_ENGINE, search_func=store.search)
        else:
            action = SearchAndSummarize()
        self._init_actions([action])
