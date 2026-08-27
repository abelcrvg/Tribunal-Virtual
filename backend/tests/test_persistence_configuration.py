from app.db_models import ProcessRecord
from app.persistence import to_domain


def test_to_domain_preserves_courtroom_configuration():
    record=ProcessRecord(number="000001-2026.TV",area="criminal",plaintiff="Autor Fictício",defendant="Réu Fictício",facts="Fatos suficientes para a simulação do processo.",include_mp=True,jury=True)
    process=to_domain(record)
    assert process.include_mp is True
    assert process.jury is True
