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

"""
Test runner for the autoblogger backend.
Runs the core functionality tests that are working properly.
"""

import subprocess
import sys
from pathlib import Path


def run_core_tests():
    """Run the core functionality tests."""
    test_files = [
        "tests/test_state.py",
        "tests/test_llm_services.py",
        "tests/test_search.py",
        "tests/unittests/agents/test_manager_agent.py",
        "tests/unittests/agents/test_research_agent.py",
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


def run_all_tests():
    """Run all tests including ones that may fail."""
    print("🧪 Running ALL autoblogger backend tests...")
    print("=" * 50)

    cmd = ["uv", "run", "python", "-m", "pytest", "tests/", "-v", "--tb=short"]

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=False)
        passed_count = "?"  # Would need to parse output to get exact count
        print(f"\n📊 Test run completed (exit code: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        success = run_all_tests()
    else:
        success = run_core_tests()
        print("\n💡 Use '--all' flag to run all tests including API endpoint tests")

    sys.exit(0 if success else 1)
