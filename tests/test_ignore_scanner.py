"""Ignore engine and scanner tests."""

from __future__ import annotations

from pathlib import Path

from ssx_header_tool.ignore import IgnoreEngine
from ssx_header_tool.scanner import RepositoryScanner


def test_default_directory_ignore(tmp_path: Path) -> None:
    target = tmp_path / "node_modules"
    target.mkdir()
    assert IgnoreEngine(tmp_path).ignored(target)


def test_gitignore_file(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("*.log\n", encoding="utf-8")
    path = tmp_path / "debug.log"
    path.touch()
    assert IgnoreEngine(tmp_path).ignored(path)


def test_ssxignore_file(tmp_path: Path) -> None:
    (tmp_path / ".ssxignore").write_text("secret.py\n", encoding="utf-8")
    path = tmp_path / "secret.py"
    path.touch()
    assert IgnoreEngine(tmp_path).ignored(path)


def test_negation(tmp_path: Path) -> None:
    (tmp_path / ".ssxignore").write_text("*.py\n!important.py\n", encoding="utf-8")
    regular = tmp_path / "regular.py"
    important = tmp_path / "important.py"
    regular.touch()
    important.touch()
    engine = IgnoreEngine(tmp_path)
    assert engine.ignored(regular)
    assert not engine.ignored(important)


def test_nested_rules(tmp_path: Path) -> None:
    child = tmp_path / "child"
    child.mkdir()
    (child / ".ssxignore").write_text("*.py\n", encoding="utf-8")
    path = child / "a.py"
    path.touch()
    engine = IgnoreEngine(tmp_path)
    engine.load_directory(child)
    assert engine.ignored(path)


def test_nested_negation_overrides_parent(tmp_path: Path) -> None:
    (tmp_path / ".ssxignore").write_text("*.py\n", encoding="utf-8")
    child = tmp_path / "child"
    child.mkdir()
    (child / ".ssxignore").write_text("!keep.py\n", encoding="utf-8")
    path = child / "keep.py"
    path.touch()
    engine = IgnoreEngine(tmp_path)
    engine.load_directory(child)
    assert not engine.ignored(path)


def test_include_patterns(tmp_path: Path) -> None:
    py = tmp_path / "a.py"
    js = tmp_path / "a.js"
    py.touch()
    js.touch()
    engine = IgnoreEngine(tmp_path, include=("*.py",))
    assert not engine.ignored(py)
    assert engine.ignored(js)


def test_exclude_patterns(tmp_path: Path) -> None:
    path = tmp_path / "generated.py"
    path.touch()
    assert IgnoreEngine(tmp_path, exclude=("generated.py",)).ignored(path)


def test_prune(tmp_path: Path) -> None:
    (tmp_path / "build").mkdir()
    (tmp_path / "src").mkdir()
    names = ["build", "src"]
    count = IgnoreEngine(tmp_path).prune(tmp_path, names)
    assert count == 1
    assert names == ["src"]


def test_scanner_supported_only(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "a.bin").write_bytes(b"text")
    scanner = RepositoryScanner(tmp_path)
    assert [entry.path.name for entry in scanner.scan()] == ["a.py"]
    assert scanner.statistics.unsupported == 1


def test_scanner_binary_detection(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_bytes(b"\x00\x01\x02")
    scanner = RepositoryScanner(tmp_path)
    assert list(scanner.scan()) == []
    assert scanner.statistics.binary == 1


def test_scanner_extension_filter(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "a.js").write_text("let a = 1;\n", encoding="utf-8")
    scanner = RepositoryScanner(tmp_path, extensions=("py",))
    assert [entry.path.suffix for entry in scanner.scan()] == [".py"]


def test_scanner_progress(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    seen: list[Path] = []
    scanner = RepositoryScanner(tmp_path, progress=lambda current, _stats: seen.append(current))
    list(scanner.scan())
    assert seen == [path]


def test_scanner_prunes_ignored_directory(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    (build / "a.py").write_text("pass\n", encoding="utf-8")
    scanner = RepositoryScanner(tmp_path)
    assert list(scanner.scan()) == []
    assert scanner.statistics.ignored == 1


def test_empty_file_is_text(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.touch()
    assert not RepositoryScanner.is_binary(path)


def test_scanner_handles_read_error(tmp_path: Path, monkeypatch: object) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    scanner = RepositoryScanner(tmp_path)
    monkeypatch.setattr(scanner, "is_binary", lambda _path: (_ for _ in ()).throw(OSError()))
    assert list(scanner.scan()) == []
    assert scanner.statistics.errors == 1
