import json
from gamma_ops.repo_eyes import scan_repository

def test_scanner_maps_nested_files_and_preserves_symlink_boundary(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('not executed')", encoding="utf-8")
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "api.schema.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".env").write_text("SHOULD_NOT_BE_HASHED", encoding="utf-8")
    (tmp_path / "linked").symlink_to(tmp_path / "src", target_is_directory=True)
    result = scan_repository(
        tmp_path, repository_name="sample/repo", branch="feature/demo",
        checkout_commit_sha="a"*40, pull_request_head_sha="b"*40,
        base_sha="c"*40, event_name="pull_request",
    )
    assert result["repository"]["name"] == "sample/repo"
    assert result["repository"]["checkout_commit_sha"] == "a"*40
    assert result["repository"]["pull_request_head_sha"] == "b"*40
    assert "checked-out working tree only" in result["repository"]["scope"]
    by_path = {row["path"]: row for row in result["entries"]}
    assert by_path["src/main.py"]["classification"] == "GREEN_READABLE_SOURCE"
    assert "L3" in by_path["src/main.py"]["onion_layers"]
    assert "L2" in by_path["schemas/api.schema.json"]["onion_layers"]
    assert by_path[".env"]["classification"] == "RED_HOLD_SENSITIVE_NAME"
    assert by_path[".env"]["sha256"] is None
    assert by_path["linked"]["classification"] == "RED_HOLD_SYMLINK"
    assert result["policy"]["source_files_executed"] is False

def test_secret_content_is_held_without_persisting_hash(tmp_path):
    secret = tmp_path / "source.txt"
    secret.write_text("-----BEGIN PRIVATE KEY-----\nsecret\n", encoding="utf-8")
    row = scan_repository(tmp_path)["entries"][0]
    assert row["classification"] == "RED_HOLD_SENSITIVE_CONTENT"
    assert row["sha256"] is None

def test_excluded_directory_and_output_path_are_respected(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("ignored", encoding="utf-8")
    (tmp_path / "ok.md").write_text("ok", encoding="utf-8")
    result = scan_repository(tmp_path)
    assert all(not row["path"].startswith(".git/") for row in result["entries"])
    assert result["files_scanned"] == 1
