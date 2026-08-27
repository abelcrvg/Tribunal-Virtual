from app.db_models import ProcessRecord, ProcessEventDB, ProcessParticipantDB

def test_process_related_models_are_registered():
    assert ProcessEventDB.__tablename__=="process_events"
    assert ProcessParticipantDB.__tablename__=="process_participants"
    assert "events" in ProcessRecord.__mapper__.relationships
    assert "participants" in ProcessRecord.__mapper__.relationships
