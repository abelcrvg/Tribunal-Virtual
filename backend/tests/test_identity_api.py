from app.participant_identity import build_user_identity
from app.courtroom import UserRole

def test_identity_display_names_are_role_specific():
    assert build_user_identity("u",UserRole.DEFENSE_ATTORNEY).display_name=="Advogado da parte ré"
    assert build_user_identity("u",UserRole.PROSECUTOR).display_name=="Representante do Ministério Público"
