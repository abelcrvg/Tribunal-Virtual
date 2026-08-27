from app.db_models import ProcessEventDB, ProcessParticipantDB

def test_event_and_participant_foreign_keys_point_to_process():
    event_fk=next(iter(ProcessEventDB.__table__.c.process_id.foreign_keys))
    participant_fk=next(iter(ProcessParticipantDB.__table__.c.process_id.foreign_keys))
    assert str(event_fk.column)=="processes.id"
    assert str(participant_fk.column)=="processes.id"
