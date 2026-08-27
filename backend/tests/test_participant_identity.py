from app.courtroom import UserRole
from app.participant_identity import build_user_identity

def test_human_identity_controls_selected_role():
    identity=build_user_identity("user-1",UserRole.PLAINTIFF_ATTORNEY)
    assert identity.is_human is True
    assert identity.controlled_role is UserRole.PLAINTIFF_ATTORNEY
    assert identity.display_name=="Advogado da parte autora"

def test_observer_cannot_be_mistaken_for_agent_role():
    identity=build_user_identity("user-2",UserRole.JUDGE)
    assert identity.is_human is True
