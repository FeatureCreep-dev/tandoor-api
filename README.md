# Tandoor API Client Auto-Publisher

Automated pipeline that generates and publishes a typed Python client for the [Tandoor Recipes](https://tandoor.dev) REST API.

The client is published to PyPI as [`tandoor-client`](https://pypi.org/project/tandoor-client/) and is updated automatically when the upstream API changes.

## Installation

```bash
pip install tandoor-client
```

## Usage

```python
from tandoor_client import Client

client = Client(base_url="https://your-tandoor-instance.com")

# Use AuthenticatedClient for endpoints requiring authentication
from tandoor_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://your-tandoor-instance.com",
    token="your-api-token",
)
```

### Example: List Recipes

```python
from tandoor_client.api.recipe import recipe_list
from tandoor_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://your-tandoor-instance.com",
    token="your-api-token",
)

response = recipe_list.sync(client=client)
```

## How It Works

A daily GitHub Actions workflow:

1. Checks for new tagged releases in the upstream Tandoor repository
2. Compares changed files against known API paths — if no API files changed, stops early
3. Extracts the OpenAPI schema via `manage.py spectacular`
4. If the schema differs from the last published version, generates a typed Python client using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
5. Publishes to PyPI via Trusted Publisher (OIDC, no stored credentials)

## Configuration

The workflow uses GitHub repository variables (no hardcoded values):

| Variable | Purpose | Example |
|----------|---------|---------|
| `UPSTREAM_REPO` | Upstream GitHub repository | `TandoorRecipes/recipes` |
| `UPSTREAM_URL` | Upstream git URL | `https://github.com/TandoorRecipes/recipes.git` |
| `API_PATHS` | Space-separated paths to check for API changes | `cookbook/serializer cookbook/views cookbook/urls` |

## Manual Trigger

```bash
gh workflow run build-and-publish.yml -f force=true
```

## License

AGPL-3.0 — matching the upstream Tandoor Recipes license.
