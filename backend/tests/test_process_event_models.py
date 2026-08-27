from app.db_models import ProcessEventDB, ProcessParticipantDB

def test_event_and_participant_foreign_keys_point_to_process():
    assert str(ProcessEventDB.__table__.c.process_id.foreign_keys.pop().target)=="processes.id"
    assert str(ProcessParticipantDB.__table__.c.process_id.foreign_keys.pop().target)=="processes.id"
