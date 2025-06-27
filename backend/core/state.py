"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# This module defines the state objects used to manage and track the progress
# of workflows, particularly focused on (today) a blogging workflow. It utilizes Pydantic
# for data validation and structuring.
#
# The module includes a base state class, `WorkflowState`, which provides
# common attributes like status, run log, and timestamp.
#
# A more specialized class, `WorkflowState`, inherits from the base class and adds fields
# specific to the blog generation process, such as the initial topic, research
# brief, sources, draft content, and final content.
#
# These state objects are designed to be passed between different agents or steps in a workflow,
# allowing each component to read from and write to a centralized state.
from enum import StrEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import datetime


class WokflowType(StrEnum):
    """Enumeration for different workflow types."""

    BLOGGING = "blogging"
    RESEARCH = "research"
    WRITING = "writing"
    EDITING = "editing"


class WorkflowState(BaseModel):
    """
    Base class for workflow state objects.
    """

    workflow_type: WokflowType = WokflowType.BLOGGING

    status: str = "PENDING"
    run_log: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

    initial_topic: str

    # used by Research Agent
    research_brief: Optional[Dict[str, Any]] = None
    sources: List[str] = Field(default_factory=list)

    # used by Writing Agent
    draft_content: Optional[str] = None

    # used by Editor Agent
    final_content: Optional[str] = None

    def log_entry(self, entry: str) -> None:
        """Adds a new entry to the run log with a timestamp."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.run_log.append(f"[{now}] {entry}")
