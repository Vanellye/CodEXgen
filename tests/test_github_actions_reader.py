from tools.eria_pantheon import github_actions_reader as reader


def test_inspection_filters_to_pinned_workflow_and_branch(monkeypatch):
    calls = []

    def fake_get(path):
        calls.append(path)
        if "/actions/workflows/" in path:
            return {
                "workflow_runs": [
                    {
                        "id": 123,
                        "path": ".github/workflows/eria-isolated-runner-validation.yml",
                        "run_number": 4,
                        "event": "workflow_dispatch",
                        "status": "completed",
                        "conclusion": "success",
                        "head_branch": reader.BRANCH,
                        "head_sha": "a" * 40,
                        "updated_at": "2026-11-14T00:00:00Z",
                        "html_url": "https://github.com/example/run/123",
                    },
                    {
                        "id": 999,
                        "path": ".github/workflows/other.yml",
                        "head_branch": reader.BRANCH,
                    },
                ]
            }
        if path.endswith("/123/artifacts?per_page=20"):
            return {"artifacts": [{"id": 7, "name": "runner-result", "size_in_bytes": 42,
                                   "expired": False}]}
        raise AssertionError("Unexpected GitHub API path: " + path)

    monkeypatch.setattr(reader, "_get", fake_get)
    result = reader.inspect_validation()

    assert result["repository"] == "Vanellye/CodEXgen"
    assert result["branch"] == reader.BRANCH
    assert result["read_only"] is True
    assert result["execution_triggered"] is False
    assert result["artifact_downloaded"] is False
    assert len(result["runs"]) == 1
    assert result["runs"][0]["head_sha"] == "a" * 40
    assert result["runs"][0]["artifacts"][0]["name"] == "runner-result"
    assert len(calls) == 2


def test_empty_run_list_is_explicit(monkeypatch):
    monkeypatch.setattr(reader, "_get", lambda path: {"workflow_runs": []})
    result = reader.inspect_validation()
    assert result["run_count"] == 0
    assert result["runs"] == []


def test_api_path_is_pinned_to_repository():
    try:
        reader._get("/repos/attacker/repo/actions/runs")
    except reader.GitHubActionsReadError as exc:
        assert "outside the configured repository" in str(exc)
    else:
        raise AssertionError("Unpinned repository path must be rejected")
