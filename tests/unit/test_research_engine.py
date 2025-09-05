import importlib
import pytest

def test_research_engine_basic_import():
    mod = importlib.import_module("src.core.automated_content_system")
    assert hasattr(mod, "ContentResearchEngine")

@pytest.mark.timeout(10)
def test_extracts_some_facts(monkeypatch):
    mod = importlib.import_module("src.core.automated_content_system")
    Engine = getattr(mod, "ContentResearchEngine")
    e = Engine()

    # Avoid live HTTP by monkeypatching _search_wikipedia to return a fallback
    monkeypatch.setattr(e, "_search_wikipedia", lambda q: [])
    # Monkeypatch wiki.page to simulate a minimal object
    class Page:
        title = "Test"
        summary = "This is a test topic."
        fullurl = "http://example.com"
        text = ("Test topic has interesting properties. "
                "It is used for unit testing. "
                "Unit tests should be deterministic. ")
        def exists(self): return True
        categories = {"Category:A": None, "Category:B": None}

    monkeypatch.setattr(e.wiki, "page", lambda topic: Page())
    data = e.research_topic("Any")
    assert data["facts"], "Expected at least one fact extracted"
    assert "title" in data and data["title"] == "Test"
