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

from .base_agent import AbstractAgent
from .editor_agent import EditorAgent
from .manager_agent import BloggerManagerAgent
from .research_agent import ResearchAgent
from .writing_agent import WritingAgent

__all__ = [
    "ResearchAgent",
    "WritingAgent",
    "EditorAgent",
    "BloggerManagerAgent",
    "AbstractAgent",
]
