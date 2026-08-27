from app.ai_assessment import Assessment

def test_assessment_contract_is_explicit():
    result=Assessment("pertinent","ai_contextual")
    assert result.label=="pertinent"
    assert result.source=="ai_contextual"
