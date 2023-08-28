#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:44
@Author  : alexanderwu
@File    : __init__.py
"""
from enum import Enum

from repolya.metagpt.actions.action import Action
from repolya.metagpt.actions.action_output import ActionOutput
from repolya.metagpt.actions.add_requirement import BossRequirement
from repolya.metagpt.actions.debug_error import DebugError
from repolya.metagpt.actions.design_api import WriteDesign
from repolya.metagpt.actions.design_api_review import DesignReview
from repolya.metagpt.actions.design_filenames import DesignFilenames
from repolya.metagpt.actions.project_management import AssignTasks, WriteTasks
from repolya.metagpt.actions.research import CollectLinks, WebBrowseAndSummarize, ConductResearch
from repolya.metagpt.actions.run_code import RunCode
from repolya.metagpt.actions.search_and_summarize import SearchAndSummarize
from repolya.metagpt.actions.write_code import WriteCode
from repolya.metagpt.actions.write_code_review import WriteCodeReview
from repolya.metagpt.actions.write_prd import WritePRD
from repolya.metagpt.actions.write_prd_review import WritePRDReview
from repolya.metagpt.actions.write_test import WriteTest


class ActionType(Enum):
    """All types of Actions, used for indexing."""

    ADD_REQUIREMENT = BossRequirement
    WRITE_PRD = WritePRD
    WRITE_PRD_REVIEW = WritePRDReview
    WRITE_DESIGN = WriteDesign
    DESIGN_REVIEW = DesignReview
    DESIGN_FILENAMES = DesignFilenames
    WRTIE_CODE = WriteCode
    WRITE_CODE_REVIEW = WriteCodeReview
    WRITE_TEST = WriteTest
    RUN_CODE = RunCode
    DEBUG_ERROR = DebugError
    WRITE_TASKS = WriteTasks
    ASSIGN_TASKS = AssignTasks
    SEARCH_AND_SUMMARIZE = SearchAndSummarize
    COLLECT_LINKS = CollectLinks
    WEB_BROWSE_AND_SUMMARIZE = WebBrowseAndSummarize
    CONDUCT_RESEARCH = ConductResearch


__all__ = [
    "ActionType",
    "Action",
    "ActionOutput",
]
