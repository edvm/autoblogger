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

from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from agents.editor_agent import EditorAgent
from agents.manager_agent import BloggerManagerAgent
from agents.research_agent import ResearchAgent
from agents.writing_agent import WritingAgent
from api.auth_strategies import AuthResult, AuthStrategyManager

# Removed ClerkUser as it's no longer in api.auth
from api.database import AuthType, User
from core.llm_services import LLMService, LLMServiceResponse, LLMUsage
from core.state import WokflowType, WorkflowState
from tools.search import SearchConfig, SearchDepth, SearchTopic, TimeRange

"""Test fixtures and builders for the autoblogger backend."""


class WorkflowStateBuilder:
    """Builder for creating WorkflowState objects for testing."""

    def __init__(self):
        self.initial_topic = "Test Topic"
        self.workflow_type = WokflowType.BLOGGING
        self.status = "PENDING"
        self.run_log = []
        self.research_brief = None
        self.sources = []
        self.draft_content = None
        self.final_content = None

    def with_topic(self, topic: str) -> "WorkflowStateBuilder":
        self.initial_topic = topic
        return self

    def with_status(self, status: str) -> "WorkflowStateBuilder":
        self.status = status
        return self

    def with_research_brief(self, brief: dict[str, Any]) -> "WorkflowStateBuilder":
        self.research_brief = brief
        return self

    def with_sources(self, sources: list) -> "WorkflowStateBuilder":
        self.sources = sources
        return self

    def with_draft_content(self, content: str) -> "WorkflowStateBuilder":
        self.draft_content = content
        return self

    def with_final_content(self, content: str) -> "WorkflowStateBuilder":
        self.final_content = content
        return self

    def with_log_entries(self, entries: list) -> "WorkflowStateBuilder":
        self.run_log = entries
        return self

    def build(self) -> WorkflowState:
        return WorkflowState(
            initial_topic=self.initial_topic,
            workflow_type=self.workflow_type,
            status=self.status,
            run_log=self.run_log,
            research_brief=self.research_brief,
            sources=self.sources,
            draft_content=self.draft_content,
            final_content=self.final_content,
        )


class MockLLMService:
    """Mock LLM service for testing."""

    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.default_response = "Mock LLM Response"
        self.call_count = 0
        self.last_prompt = None
        self.last_system_message = None

    def generate_response(
        self,
        prompt: str,
        system_message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMServiceResponse:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system_message = system_message

        # Check if we have a specific response for this prompt
        content = self.responses.get(prompt, self.default_response)
        usage = LLMUsage(total_tokens=100)

        return LLMServiceResponse(content=content, usage=usage)


class MockSearchTool:
    """Mock search tool for testing."""

    def __init__(self, results: dict[str, Any] | None = None):
        self.results = results or self._default_results()
        self.search_count = 0
        self.last_query = None
        self.last_config = None

    def search(self, query: str, search_config: SearchConfig) -> dict[str, Any]:
        self.search_count += 1
        self.last_query = query
        self.last_config = search_config
        return self.results

    @staticmethod
    def _default_results() -> dict[str, Any]:
        return {
            "results": [
                {
                    "title": "Test Article 1",
                    "url": "https://example.com/article1",
                    "content": "This is test content for article 1.",
                    "score": 0.9,
                },
                {
                    "title": "Test Article 2",
                    "url": "https://example.com/article2",
                    "content": "This is test content for article 2.",
                    "score": 0.8,
                },
            ],
            "query": "test query",
            "response_time": 1.2,
        }


class MockAgent:
    """Mock agent for testing workflow orchestration."""

    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.executed = False
        self.received_state = None

    def execute(self, state: WorkflowState) -> WorkflowState:
        self.executed = True
        self.received_state = state

        if self.should_fail:
            raise Exception(f"{self.name} agent failed")

        # Update state based on agent type
        if "research" in self.name.lower():
            state.research_brief = {"main_points": ["Point 1", "Point 2"]}
            state.sources = ["https://example.com/source1"]
        elif "writing" in self.name.lower():
            state.draft_content = f"Draft content from {self.name}"
        elif "editor" in self.name.lower():
            state.final_content = f"Final content from {self.name}"

        state.log_entry(f"{self.name} agent executed successfully")
        return state


@pytest.fixture
def workflow_state_builder():
    """Fixture providing a WorkflowState builder."""
    return WorkflowStateBuilder()


@pytest.fixture
def basic_workflow_state():
    """Fixture providing a basic WorkflowState."""
    return WorkflowStateBuilder().with_topic("Test Blog Topic").build()


@pytest.fixture
def researched_workflow_state():
    """Fixture providing a WorkflowState with research completed."""
    research_brief = {
        "main_points": [
            "AI is transforming industries",
            "Machine learning adoption is growing",
        ],
        "statistics": ["80% of companies use AI", "ML market grew 40% in 2023"],
        "quotes": ["AI will revolutionize everything - Expert"],
        "counter_arguments": ["AI adoption faces privacy concerns"],
    }

    return (
        WorkflowStateBuilder()
        .with_topic("AI Technology Trends")
        .with_status("RESEARCHING")
        .with_research_brief(research_brief)
        .with_sources(
            ["https://example.com/ai-trends", "https://example.com/ml-growth"]
        )
        .build()
    )


@pytest.fixture
def draft_written_workflow_state():
    """Fixture providing a WorkflowState with draft content."""
    return (
        WorkflowStateBuilder()
        .with_topic("AI Technology Trends")
        .with_status("WRITING")
        .with_research_brief({"main_points": ["AI is growing"]})
        .with_sources(["https://example.com/source"])
        .with_draft_content("# AI Technology Trends\n\nAI is rapidly transforming...")
        .build()
    )


@pytest.fixture
def completed_workflow_state():
    """Fixture providing a completed WorkflowState."""
    return (
        WorkflowStateBuilder()
        .with_topic("AI Technology Trends")
        .with_status("COMPLETED")
        .with_research_brief({"main_points": ["AI is growing"]})
        .with_sources(["https://example.com/source"])
        .with_draft_content("# AI Technology Trends\n\nAI is rapidly transforming...")
        .with_final_content(
            "# AI Technology Trends\n\nArtificial intelligence is revolutionizing..."
        )
        .build()
    )


@pytest.fixture
def mock_llm_service(mocker):
    """Fixture providing a mock LLM service."""
    mock = mocker.Mock(spec=LLMService)
    mock.generate_response.return_value = LLMServiceResponse(
        content="Mock LLM Response", usage=LLMUsage(total_tokens=100)
    )
    return mock


@pytest.fixture
def mock_search_tool(mocker):
    """Fixture providing a mock search tool."""
    return MockSearchTool()


@pytest.fixture
def search_config():
    """Fixture providing a basic search configuration."""
    return SearchConfig(
        search_depth=SearchDepth.BASIC,
        topic=SearchTopic.GENERAL,
        time_range=TimeRange.MONTH,
        max_results=5,
    )


@pytest.fixture
def mock_research_agent():
    """Fixture providing a mock research agent."""
    return MockAgent("Research")


@pytest.fixture
def mock_writing_agent():
    """Fixture providing a mock writing agent."""
    return MockAgent("Writing")


@pytest.fixture
def mock_editor_agent():
    """Fixture providing a mock editor agent."""
    return MockAgent("Editor")


@pytest.fixture
def mock_failing_research_agent():
    """Fixture providing a mock research agent that fails."""
    return MockAgent("Research", should_fail=True)


@pytest.fixture
def research_agent(mock_llm_service, mock_search_tool, search_config):
    """Fixture providing a real research agent with mocked dependencies."""
    return ResearchAgent(
        llm_service=mock_llm_service,
        search_tool=mock_search_tool,
        search_config=search_config,
    )


@pytest.fixture
def writing_agent(mock_llm_service):
    """Fixture providing a real writing agent with mocked dependencies."""
    return WritingAgent(llm_service=mock_llm_service)


@pytest.fixture
def editor_agent(mock_llm_service):
    """Fixture providing a real editor agent with mocked dependencies."""
    return EditorAgent(llm_service=mock_llm_service)


@pytest.fixture
def blogger_manager_agent(mock_research_agent, mock_writing_agent, mock_editor_agent):
    """Fixture providing a blogger manager agent with mocked sub-agents."""
    return BloggerManagerAgent(
        research_agent=mock_research_agent,
        writing_agent=mock_writing_agent,
        editor_agent=mock_editor_agent,
    )


# Test Authentication Utilities
def create_mock_user(
    id: int = 1,
    user_id: int = None,  # Keep for backward compatibility
    clerk_user_id: str = "test_clerk_user_123",
    email: str = "test@example.com",
    username: str = None,
    first_name: str = "Test",
    last_name: str = "User",
    credits: int = 100,
    is_active: bool = True,
) -> Mock:
    """Create a mock User object for testing."""
    from datetime import datetime

    mock_user = Mock(spec=User)
    mock_user.id = id if user_id is None else user_id
    mock_user.clerk_user_id = clerk_user_id
    mock_user.email = email
    mock_user.username = username
    mock_user.first_name = first_name
    mock_user.last_name = last_name
    mock_user.credits = credits
    mock_user.is_active = is_active
    mock_user.created_at = datetime(2024, 1, 1, 0, 0, 0)
    mock_user.updated_at = datetime(2024, 1, 1, 0, 0, 0)
    return mock_user


def create_mock_clerk_user(
    user_id: str = "test_clerk_user_123",
    email: str = "test@example.com",
    first_name: str = "Test",
    last_name: str = "User",
) -> Mock:
    """Create a mock ClerkUser object for testing."""
    mock_clerk_user = Mock()
    mock_clerk_user.user_id = user_id
    mock_clerk_user.email = email
    mock_clerk_user.first_name = first_name
    mock_clerk_user.last_name = last_name
    return mock_clerk_user


@pytest.fixture
def mock_test_user():
    """Fixture providing a mock test user."""
    return create_mock_user()


@pytest.fixture
def mock_test_clerk_user():
    """Fixture providing a mock test clerk user."""
    return create_mock_clerk_user()


@pytest.fixture
def authenticated_client(mock_test_user):
    """Fixture providing an authenticated test client with mock database (legacy)."""
    from api.auth import get_current_user
    from api.database import User, get_db
    from api.main import app

    # Override the get_current_user dependency
    def get_current_user_override():
        return mock_test_user

    # Override the get_db dependency to return a mock
    def get_db_override():
        return Mock()

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client_with_real_db(test_database_session):
    """Fixture providing an authenticated test client with real database session."""
    from api.auth import get_current_user
    from api.database import get_db
    from api.main import app
    from tests.utils.auth_test_utils import UserFactory

    # Create a real user in the test database
    test_user = UserFactory.create_system_user(
        id=1,
        system_user_id=1,
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        credits=100,
    )
    test_database_session.add(test_user)
    test_database_session.commit()

    # Override dependencies
    def get_current_user_override():
        return test_user

    def get_db_override():
        return test_database_session

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client_with_custom_user():
    """Fixture factory for creating authenticated client with custom user (legacy mock version)."""
    created_clients = []

    def _create_client(user: Mock = None, clerk_user=None):
        from api.auth import get_current_user
        from api.database import get_db
        from api.main import app

        test_user = user or create_mock_user()

        # Clear any existing overrides first
        app.dependency_overrides.clear()

        # Override the get_current_user dependency
        def get_current_user_override():
            return test_user

        # Override the get_db dependency to return a mock
        def get_db_override():
            return Mock()

        app.dependency_overrides[get_current_user] = get_current_user_override
        app.dependency_overrides[get_db] = get_db_override

        client = TestClient(app)
        created_clients.append(client)
        return client

    yield _create_client

    # Clean up after all tests are done
    from api.main import app

    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client_with_real_db_factory(test_database_session):
    """Fixture factory for creating authenticated clients with real database and custom users."""
    created_clients = []

    def _create_client(user_data: dict = None, auth_type=None):
        from api.auth import get_current_user
        from api.database import get_db, AuthType
        from api.main import app
        from tests.utils.auth_test_utils import UserFactory

        # Set default user data
        default_user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "credits": 100,
        }
        
        if user_data:
            default_user_data.update(user_data)
        
        # Create user based on auth type
        if auth_type == AuthType.CLERK:
            test_user = UserFactory.create_clerk_user(
                clerk_user_id="clerk_user_123",
                **default_user_data
            )
        else:
            test_user = UserFactory.create_system_user(
                system_user_id=1,
                **default_user_data
            )

        test_database_session.add(test_user)
        test_database_session.commit()

        # Clear any existing overrides first
        app.dependency_overrides.clear()

        # Override dependencies
        def get_current_user_override():
            return test_user

        def get_db_override():
            return test_database_session

        app.dependency_overrides[get_current_user] = get_current_user_override
        app.dependency_overrides[get_db] = get_db_override

        client = TestClient(app)
        created_clients.append((client, test_user))
        return client

    yield _create_client

    # Clean up after all tests are done
    from api.main import app
    app.dependency_overrides.clear()


# New Authentication Test Fixtures


@pytest.fixture(scope="function")
def test_database_engine():
    """Fixture providing a test database engine for each test."""
    from sqlalchemy import create_engine
    
    # Import all models to ensure they're registered with Base.metadata
    # This is critical - all models must be imported before create_all()
    from api.database import (
        Base, 
        User, 
        CreditTransaction, 
        AppUsage, 
        SystemUser, 
        ApiKey,
        # Import any additional models that might exist
    )

    # Create in-memory SQLite database for testing
    # Using a file:// URI with a unique name to share between connections
    import uuid
    db_name = f"test_db_{uuid.uuid4().hex}"
    engine = create_engine(
        f"sqlite:///{db_name}.db",
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )
    
    # Ensure all tables are created
    Base.metadata.create_all(engine)
    
    # Verify tables were created (for debugging)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = ["users", "system_users", "api_keys", "credit_transactions", "app_usages"]
    for table in expected_tables:
        if table not in tables:
            raise RuntimeError(f"Table '{table}' was not created in test database")
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()
    
    # Remove the test database file
    import os
    try:
        os.unlink(f"{db_name}.db")
    except OSError:
        pass  # File may not exist


@pytest.fixture(scope="function")
def test_database_session(test_database_engine):
    """Fixture providing an in-memory test database session with automatic cleanup."""
    from sqlalchemy.orm import sessionmaker

    TestSession = sessionmaker(bind=test_database_engine)
    session = TestSession()

    yield session

    session.close()


@pytest.fixture(scope="function")
def test_database_session_transactional(test_database_engine):
    """Fixture providing a transactional test database session that rolls back after each test."""
    from sqlalchemy.orm import sessionmaker

    TestSession = sessionmaker(bind=test_database_engine)
    session = TestSession()
    
    # Start a transaction
    transaction = session.begin()
    
    yield session
    
    # Rollback the transaction to ensure clean state
    transaction.rollback()
    session.close()


@pytest.fixture
def system_user_factory():
    """Fixture providing SystemUser factory."""
    from tests.utils.auth_test_utils import SystemUserFactory

    return SystemUserFactory


@pytest.fixture
def api_key_factory():
    """Fixture providing ApiKey factory."""
    from tests.utils.auth_test_utils import ApiKeyFactory

    return ApiKeyFactory


@pytest.fixture
def user_factory():
    """Fixture providing User factory."""
    from tests.utils.auth_test_utils import UserFactory

    return UserFactory


@pytest.fixture
def auth_test_data():
    """Fixture providing authentication test data."""
    from tests.utils.auth_test_utils import AuthTestData

    return AuthTestData


@pytest.fixture
def auth_test_helpers():
    """Fixture providing authentication test helpers."""
    from tests.utils.auth_test_utils import AuthTestHelpers

    return AuthTestHelpers


@pytest.fixture
def mock_system_user():
    """Fixture providing a mock system user."""
    from tests.utils.auth_test_utils import SystemUserFactory

    return SystemUserFactory.create_mock_system_user()


@pytest.fixture
def mock_api_key():
    """Fixture providing a mock API key."""
    from tests.utils.auth_test_utils import ApiKeyFactory

    return ApiKeyFactory.create_mock_api_key()


@pytest.fixture
def mock_system_auth_user():
    """Fixture providing a mock User with system authentication."""
    from tests.utils.auth_test_utils import UserFactory

    return UserFactory.create_mock_user(auth_type=AuthType.SYSTEM)


@pytest.fixture
def mock_clerk_auth_user():
    """Fixture providing a mock User with Clerk authentication."""
    from tests.utils.auth_test_utils import UserFactory

    return UserFactory.create_mock_user(
        auth_type=AuthType.CLERK, clerk_user_id="clerk_user_123", system_user_id=None
    )


@pytest.fixture
def test_api_key_pair():
    """Fixture providing a test API key and its hash."""
    from tests.utils.auth_test_utils import ApiKeyFactory

    return ApiKeyFactory.generate_test_api_key()


@pytest.fixture
def authenticated_api_key_client(test_database_session):
    """Fixture providing an authenticated test client using API key with real database."""
    from fastapi.testclient import TestClient

    from api.auth import get_current_user
    from api.database import get_db
    from api.main import app
    from tests.utils.auth_test_utils import UserFactory, SystemUserFactory

    # Create a real system user and user in the test database
    system_user = SystemUserFactory.create_system_user(
        id=1,
        username="testuser",
        email="test@example.com",
        password="testpassword123",
    )
    test_database_session.add(system_user)
    test_database_session.commit()

    test_user = UserFactory.create_system_user(
        id=1,
        system_user_id=system_user.id,
        email="test@example.com",
        username="testuser",
    )
    test_database_session.add(test_user)
    test_database_session.commit()

    # Override dependencies
    def get_current_user_override():
        return test_user

    def get_db_override():
        return test_database_session

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)

    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_clerk_client(test_database_session):
    """Fixture providing an authenticated test client using Clerk with real database."""
    from fastapi.testclient import TestClient

    from api.auth import get_current_user
    from api.database import get_db
    from api.main import app
    from tests.utils.auth_test_utils import UserFactory

    # Create a real Clerk user in the test database
    test_user = UserFactory.create_clerk_user(
        id=1,
        clerk_user_id="clerk_user_123",
        email="clerk@example.com",
        username="clerkuser",
    )
    test_database_session.add(test_user)
    test_database_session.commit()

    # Override dependencies
    def get_current_user_override():
        return test_user

    def get_db_override():
        return test_database_session

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)

    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_strategy_manager():
    """Fixture providing a mock AuthStrategyManager."""
    from tests.utils.auth_test_utils import UserFactory

    mock_manager = Mock(spec=AuthStrategyManager)

    # Default successful authentication
    mock_auth_result = AuthResult(
        user=UserFactory.create_mock_user(),
        auth_type=AuthType.SYSTEM,
        metadata={"api_key_id": 1},
    )
    mock_manager.authenticate = Mock(return_value=mock_auth_result)

    return mock_manager
