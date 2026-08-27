from app.judicial_review import JudicialReview

def test_judicial_review_contract():
    result=JudicialReview("CONCEDER_PALAVRA","A palavra é concedida.","fallback","deterministic")
    assert result.action=="CONCEDER_PALAVRA"
    assert result.provider=="fallback"
