from app.courtroom import InterventionAssessment, UserRole, assess_intervention, build_courtroom


def test_out_of_turn_irrelevant_is_rejected():
    result = assess_intervention(role=UserRole.DEFENSE_ATTORNEY.value, turn_role=UserRole.PLAINTIFF_ATTORNEY.value, content="Não concordo.")
    assert result.allowed is False
    assert result.assessment is InterventionAssessment.IRRELEVANT
    assert result.requires_record is False


def test_out_of_turn_relevant_can_be_admitted():
    result = assess_intervention(role=UserRole.DEFENSE_ATTORNEY.value, turn_role=UserRole.PLAINTIFF_ATTORNEY.value, content="O documento original apresentado contradiz o depoimento da testemunha e demonstra que o contrato juntado aos autos possui data incompatível.")
    assert result.allowed is True
    assert result.requires_record is True
    assert result.assessment in {InterventionAssessment.PERTINENT, InterventionAssessment.DECISIVE}


def test_abusive_intervention_is_blocked():
    result = assess_intervention(role=UserRole.DEFENSE_ATTORNEY.value, turn_role=UserRole.PLAINTIFF_ATTORNEY.value, content="Cala a boca, idiota.")
    assert result.allowed is False
    assert result.assessment is InterventionAssessment.ABUSIVE


def test_courtroom_generates_jury_and_mp():
    participants = build_courtroom(include_mp=True, jury=True)
    roles = [participant.role for participant in participants]
    assert roles.count(UserRole.JUDGE) == 1
    assert roles.count(UserRole.PLAINTIFF_ATTORNEY) == 1
    assert roles.count(UserRole.DEFENSE_ATTORNEY) == 1
    assert roles.count(UserRole.PROSECUTOR) == 1
    assert roles.count(UserRole.JUROR) == 7
    assert all(participant.fictional for participant in participants)
