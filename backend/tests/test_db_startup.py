from app.database import Base
import app.db_models

def test_all_process_relationship_targets_are_registered():
    mapper=Base.registry.mappers
    names={m.class_.__name__ for m in mapper}
    assert "ProcessRecord" in names
    assert "ProcessEventDB" in names
    assert "ProcessParticipantDB" in names
