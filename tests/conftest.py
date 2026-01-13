"""
Общие фикстуры для тестов.
"""
import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_ibeam_params():
    """Параметры типового двутавра для тестов."""
    return {
        "h_mm": 200,
        "b_mm": 100,
        "tw_mm": 6,
        "tf_mm": 10
    }


@pytest.fixture
def sample_rect_tube_params():
    """Параметры типовой прямоугольной трубы для тестов."""
    return {
        "h_mm": 150,
        "b_mm": 100,
        "t_mm": 5
    }


@pytest.fixture
def sample_circ_tube_params():
    """Параметры типовой круглой трубы для тестов."""
    return {
        "d_mm": 100,
        "t_mm": 5
    }


@pytest.fixture
def sample_material():
    """Параметры типового материала для тестов."""
    return {
        "steel_grade": "C245",
        "ry_mpa": 245,
        "e_mpa": 206000
    }


@pytest.fixture
def sample_compression_params():
    """Параметры для расчета на сжатие."""
    return {
        "l_geo_m": 3.0,
        "mu": 1.0
    }
