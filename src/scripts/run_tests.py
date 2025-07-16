#!/usr/bin/env python3
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

import subprocess
import sys
from pathlib import Path

"""
Test runner for the autoblogger backend.
Runs the core functionality tests that are working properly.
"""


def run_core_tests():
    """Run the core functionality tests."""
    test_files = [
        # Core services
        "tests/test_state.py",
        "tests/test_llm_services.py",
        "tests/test_search.py",
        
        # Authentication and security
        "tests/test_auth_security.py",
        "tests/test_auth_strategies.py",
        
        # Agent tests
        "tests/unittests/agents/test_manager_agent.py",
        "tests/unittests/agents/test_research_agent.py",
        "tests/unittests/agents/test_writing_agent.py",
        "tests/unittests/agents/test_editor_agent.py",
    ]

    print("🧪 Running core autoblogger backend tests...")
    print("=" * 50)

    cmd = ["uv", "run", "python", "-m", "pytest"] + test_files + ["-v"]

    try:
        subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=True)
        print("\n✅ All core tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Some tests failed (exit code: {e.returncode})")
        return False


def run_api_tests():
    """Run API and system tests (may require setup)."""
    api_test_files = [
        "tests/test_api_endpoints.py",
        "tests/test_system_auth_endpoints.py",
        "tests/test_system_auth_models.py",
    ]
    
    print("🔗 Running API and system tests...")
    print("=" * 50)
    print("⚠️  Note: These tests may require proper environment setup")
    
    cmd = ["uv", "run", "python", "-m", "pytest"] + api_test_files + ["-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=False)
        print(f"\n📊 API test run completed (exit code: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"\n❌ Error running API tests: {e}")
        return False


def run_all_tests():
    """Run all tests including ones that may fail."""
    print("🧪 Running ALL autoblogger backend tests...")
    print("=" * 50)

    cmd = ["uv", "run", "python", "-m", "pytest", "tests/", "-v", "--tb=short"]

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=False)
        print(f"\n📊 Test run completed (exit code: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            success = run_all_tests()
        elif sys.argv[1] == "--api":
            success = run_api_tests()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Test Runner for AutoBlogger Backend")
            print("=" * 40)
            print("Usage:")
            print("  python run_tests.py          # Run core functionality tests (default)")
            print("  python run_tests.py --api    # Run API and system tests only")
            print("  python run_tests.py --all    # Run all tests")
            print("  python run_tests.py --help   # Show this help")
            print("\nTest Categories:")
            print("  Core: Basic functionality, services, agents (stable)")
            print("  API:  Endpoint and system tests (may need setup)")
            print("  All:  Everything including potentially unstable tests")
            sys.exit(0)
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        success = run_core_tests()
        print("\n💡 Available options:")
        print("  --api    Run API tests only")
        print("  --all    Run all tests")
        print("  --help   Show detailed help")

    sys.exit(0 if success else 1)
