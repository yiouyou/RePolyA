#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anthropic
from anthropic import Anthropic

from metagpt.config import CONFIG


class Claude2:
    def ask(self, prompt):
        client = Anthropic(api_key=CONFIG.claude_api_key)

        res = client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            max_tokens_to_sample=1000,
        )
        return res.completion

    async def aask(self, prompt):
        client = Anthropic(api_key=CONFIG.claude_api_key)

        res = client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            max_tokens_to_sample=1000,
        )
        return res.completion
