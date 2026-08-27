from app.courtroom import assess_intervention


def test_out_of_turn_irrelevant_is_reprimanded():
    result = assess_intervention(role="defense_attorney", turn_role="plaintiff_attorney", content="Não concordo.")
    assert result.allowed is False
    assert result.requires_record is False


def test_out_of_turn_relevant_can_be_admitted():
    result = assess_intervention(role="defense_attorney", turn_role="plaintiff_attorney", content="O documento apresentado contradiz o depoimento da testemunha e demonstra que o contrato juntado aos autos possui data incompatível.")
    assert result.allowed is True
    assert result.requires_record is True
    assert result.assessment.value in {"pertinent", "decisive"}


def test_abusive_intervention_is_blocked():
    result = assess_intervention(role="defense_attorney", turn_role="plaintiff_attorney", content="Cala a boca, idiota.")
    assert result.allowed is False
    assert result.assessment.value == "abusive"
