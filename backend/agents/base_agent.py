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

from abc import ABC, abstractmethod
from core.state import WorkflowState


class AbstractAgent(ABC):
    """Abstract base class for all agents."""

    @abstractmethod
    def execute(self: "AbstractAgent", state: WorkflowState) -> WorkflowState:
        """Executes the agent's specific task.

        Args:
            state: The current state of the workflow.

        Returns:
            The updated state after the agent's task is completed.
        """
        pass
