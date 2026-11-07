"""Tests for FileService and path collision management."""

from app.services.file_service import FileService


def test_unique_filepath_when_not_exists(tmp_path):
    target = tmp_path / "video.mp4"
    unique = FileService.get_unique_filepath(target)
    assert unique == target


def test_unique_filepath_when_exists(tmp_path):
    target = tmp_path / "video.mp4"
    target.write_text("dummy")

    unique1 = FileService.get_unique_filepath(target)
    assert unique1.name == "video (1).mp4"

    unique1.write_text("dummy 2")
    unique2 = FileService.get_unique_filepath(target)
    assert unique2.name == "video (2).mp4"


def test_delete_file_safely(tmp_path):
    target = tmp_path / "delete_me.txt"
    target.write_text("test")
    assert target.exists()

    deleted = FileService.delete_file_safely(target)
    assert deleted
    assert not target.exists()

    # Second delete on non-existent file returns False safely
    assert not FileService.delete_file_safely(target)


def test_get_file_size(tmp_path):
    target = tmp_path / "sample.bin"
    target.write_bytes(b"1234567890")
    assert FileService.get_file_size(target) == 10
