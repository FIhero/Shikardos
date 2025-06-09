from pathlib import Path
from typing import Iterator, Tuple
from unittest.mock import MagicMock, patch

import pytest

from src.utils import load_transactions


@pytest.fixture
def mock_file_system() -> Iterator[Tuple[MagicMock, MagicMock]]:
    """Фикстура для мокинга файловой системы"""
    with patch.object(Path, "is_file") as mock_is_file, patch.object(Path, "open") as mock_open:
        yield mock_is_file, mock_open


def test_load_valid_json_array(mock_file_system: Tuple[MagicMock, MagicMock]) -> None:
    mock_is_file, mock_open = mock_file_system
    mock_is_file.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = '[{"id": 1}]'

    result = load_transactions("valid.json")
    assert result == [{"id": 1}]


def test_load_non_array_json(mock_file_system: Tuple[MagicMock, MagicMock]) -> None:
    mock_is_file, mock_open = mock_file_system
    mock_is_file.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = '{"id": 1}'

    result = load_transactions("not_array.json")
    assert result == []


def test_file_not_exists(mock_file_system: Tuple[MagicMock, MagicMock]) -> None:
    mock_is_file, _ = mock_file_system
    mock_is_file.return_value = False

    result = load_transactions("nonexistent.json")
    assert result == []


def test_invalid_json(mock_file_system: Tuple[MagicMock, MagicMock]) -> None:
    mock_is_file, mock_open = mock_file_system
    mock_is_file.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = "invalid"

    result = load_transactions("invalid.json")
    assert result == []


def test_io_error(mock_file_system: Tuple[MagicMock, MagicMock]) -> None:
    mock_is_file, mock_open = mock_file_system
    mock_is_file.return_value = True
    mock_open.side_effect = OSError("Read error")

    result = load_transactions("error.json")
    assert result == []
