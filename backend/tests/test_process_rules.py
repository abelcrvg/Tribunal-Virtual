from app.models import CaseArea, ProcessCreate, ProcessStatus


def test_process_accepts_jury_configuration():
    process = ProcessCreate(area=CaseArea.CRIMINAL, plaintiff="Ministério Público", defendant="João da Silva", facts="A denúncia descreve fatos que serão analisados durante a instrução criminal.", include_mp=True, jury=True)
    assert process.jury is True
    assert process.include_mp is True


def test_initial_status_is_created():
    assert ProcessStatus.CREATED.value == "created"
