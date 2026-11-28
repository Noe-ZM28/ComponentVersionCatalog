from app.repositories import external_repository


def test_component_loader_uses_normal_stored_procedure_by_default(
    monkeypatch,
    ):
    calls = []
    monkeypatch.setattr(
        external_repository.settings,
        "use_dummy_stored_procedures",
        False,
    )
    monkeypatch.setattr(
        external_repository,
        "exec_store_procedure",
        lambda procedure, parameters: calls.append((procedure, parameters)) or [],
    )

    external_repository.get_dialogues_list("123")

    assert calls == [
        ("[CDSPLUSP].[dbo].[SP_GetDialogues]", {"CustNum": "123"})
    ]


def test_component_loader_uses_dummy_stored_procedure_when_enabled(
    monkeypatch,
    ):
    calls = []
    monkeypatch.setattr(
        external_repository.settings,
        "use_dummy_stored_procedures",
        True,
    )
    monkeypatch.setattr(
        external_repository,
        "exec_store_procedure",
        lambda procedure, parameters: calls.append((procedure, parameters)) or [],
    )

    external_repository.get_dialogues_list("123")

    assert calls == [
        ("[CDSPLUSP].[dbo].[SP_GetDialoguesDummy]", {"CustNum": "123"})
    ]
