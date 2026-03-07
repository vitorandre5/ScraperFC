"""API routers package."""
from app.api import (
    routes_health,
    routes_sports,
    routes_leagues,
    routes_teams,
    routes_matches,
    routes_sync,
)

__all__ = [
    "routes_health",
    "routes_sports",
    "routes_leagues",
    "routes_teams",
    "routes_matches",
    "routes_sync",
]
