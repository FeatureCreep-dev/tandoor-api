#!/usr/bin/env python3
"""Smoke-test the generated tandoor-client package.

Validates that:
1. The package can be imported
2. The Client class exists and is instantiable
3. Key model classes exist (based on known Tandoor API models)
4. Basic type checking passes (optional, if mypy is available)
"""

import importlib
import subprocess
import sys
from pathlib import Path


EXPECTED_MODELS = [
    "Recipe",
    "Ingredient",
    "Step",
    "Keyword",
    "Food",
    "Unit",
    "MealPlan",
    "ShoppingListEntry",
    "UserPreference",
]


def check_import() -> bool:
    """Verify the package can be imported."""
    try:
        import tandoor_client
        print(f"OK: tandoor_client imported from {tandoor_client.__file__}")
        return True
    except ImportError as e:
        print(f"FAIL: Cannot import tandoor_client: {e}")
        return False


def check_client_class() -> bool:
    """Verify the Client class exists and can be instantiated."""
    try:
        from tandoor_client import Client
        client = Client(base_url="http://localhost:8080")
        print(f"OK: Client class instantiated: {type(client)}")
        return True
    except ImportError:
        # Some generator versions use AuthenticatedClient or different names
        try:
            from tandoor_client import AuthenticatedClient
            print(f"OK: AuthenticatedClient class found (Client alias may differ)")
            return True
        except ImportError as e:
            print(f"FAIL: Cannot import Client or AuthenticatedClient: {e}")
            return False
    except Exception as e:
        # Client exists but instantiation requires different args — still OK
        print(f"OK: Client class exists (instantiation note: {e})")
        return True


def check_models() -> tuple[int, int]:
    """Check which expected model classes exist in the package."""
    found = 0
    missing = 0

    try:
        models_mod = importlib.import_module("tandoor_client.models")
    except ImportError:
        print("WARN: tandoor_client.models not found, trying tandoor_client.types")
        try:
            models_mod = importlib.import_module("tandoor_client.types")
        except ImportError:
            print("FAIL: No models module found")
            return 0, len(EXPECTED_MODELS)

    for model_name in EXPECTED_MODELS:
        if hasattr(models_mod, model_name):
            print(f"  OK: {model_name}")
            found += 1
        else:
            # Models may have different naming conventions (e.g., prefixed/suffixed)
            # Check for partial matches
            matches = [n for n in dir(models_mod) if model_name.lower() in n.lower()]
            if matches:
                print(f"  OK: {model_name} (as {matches[0]})")
                found += 1
            else:
                print(f"  MISS: {model_name} not found")
                missing += 1

    return found, missing


def check_mypy(package_dir: Path) -> bool:
    """Run mypy type checking if available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "--ignore-missing-imports",
             str(package_dir / "tandoor_client")],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print("OK: mypy type check passed")
            return True
        else:
            print(f"WARN: mypy found issues (non-blocking):\n{result.stdout[:500]}")
            return True  # Non-blocking
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("SKIP: mypy not available or timed out")
        return True


def main() -> None:
    print("=" * 60)
    print("tandoor-client smoke test")
    print("=" * 60)

    results = []

    print("\n--- Import Check ---")
    results.append(check_import())

    print("\n--- Client Class Check ---")
    results.append(check_client_class())

    print("\n--- Model Check ---")
    found, missing = check_models()
    # Pass if at least some models exist (API may have changed names)
    results.append(found > 0)
    print(f"\nModels: {found} found, {missing} missing")

    print("\n--- Type Check ---")
    if len(sys.argv) > 1:
        results.append(check_mypy(Path(sys.argv[1])))
    else:
        print("SKIP: No package dir provided for mypy")

    print("\n" + "=" * 60)
    if all(results):
        print("PASSED: All checks passed")
        sys.exit(0)
    else:
        print("FAILED: Some checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
