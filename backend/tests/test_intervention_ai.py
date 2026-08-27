from app.intervention_ai import assess_with_context

def test_fallback_is_safe_without_provider(monkeypatch):
    class Provider:
        def generate(self,**kwargs): raise RuntimeError("offline")
    monkeypatch.setattr("app.intervention_ai.get_provider",lambda:Provider())
    assert assess_with_context("oi","fatos",[],"opening")=="normal"
