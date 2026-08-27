from app.judicial_review import review_intervention

def test_fallback_maps_relevant_intervention_to_floor_action(monkeypatch):
    class Provider:
        def generate(self,**kwargs): raise RuntimeError("offline")
    monkeypatch.setattr("app.judicial_review.get_provider",lambda:Provider())
    result=review_intervention(content="A prova contradiz a alegação.",assessment="pertinent",facts={"events":[]},history=[],phase="defense")
    assert result.action=="CONCEDER_PALAVRA"
    assert result.provider=="fallback"
