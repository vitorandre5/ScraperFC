"""Public package API for ScraperFC.

Uses lazy imports so importing `ScraperFC` does not eagerly import every
provider and heavy dependency at process startup.
"""

from importlib import import_module

__all__ = ["Capology", "ClubElo", "FBref", "Sofascore", "Transfermarkt", "Understat", "utils"]


def __getattr__(name):
	if name == "Capology":
		return import_module(".capology", __name__).Capology
	if name == "ClubElo":
		return import_module(".clubelo", __name__).ClubElo
	if name == "FBref":
		return import_module(".fbref", __name__).FBref
	if name == "Sofascore":
		return import_module(".sofascore", __name__).Sofascore
	if name == "Transfermarkt":
		return import_module(".transfermarkt", __name__).Transfermarkt
	if name == "Understat":
		return import_module(".understat", __name__).Understat
	if name == "utils":
		return import_module(".utils", __name__)
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
