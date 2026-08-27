from app.judge_review import JudicialReview

def test_judicial_review_contract():
    review=JudicialReview("pertinent","Relacionada à prova documental.",None)
    assert review.classification=="pertinent"
    assert "prova" in review.reasoning
