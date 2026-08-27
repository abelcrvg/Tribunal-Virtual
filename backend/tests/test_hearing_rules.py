from app.hearing_rules import decide_intervention, InterventionDisposition

def test_authorized_turn_is_admitted():
    d=decide_intervention(True,"normal")
    assert d.disposition is InterventionDisposition.ADMIT

def test_relevant_interruption_is_registered():
    d=decide_intervention(False,"pertinent")
    assert d.disposition is InterventionDisposition.REGISTER
    assert d.requires_ruling

def test_irrelevant_interruption_is_reprimanded():
    d=decide_intervention(False,"normal")
    assert d.disposition is InterventionDisposition.REPRIMAND
