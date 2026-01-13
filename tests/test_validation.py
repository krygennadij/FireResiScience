"""
Тесты для модуля валидации входных данных.
"""
import pytest
from src.validation import (
    ValidationError,
    validate_positive,
    validate_ibeam_geometry,
    validate_channel_geometry,
    validate_rect_tube_geometry,
    validate_circ_tube_geometry,
    validate_angle_geometry,
    validate_load,
    validate_bending_load,
    validate_material,
    validate_geometric_length,
    validate_all_inputs
)


class TestValidatePositive:
    """Тесты для функции validate_positive."""

    def test_valid_positive_value(self):
        """Проверка корректного положительного значения."""
        # Не должно вызвать исключение
        validate_positive(10.0, "Тест", min_value=0, max_value=100)

    def test_none_value(self):
        """Проверка на None."""
        with pytest.raises(ValidationError, match="значение не может быть пустым"):
            validate_positive(None, "Тест")

    def test_zero_value(self):
        """Проверка нулевого значения."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_positive(0, "Тест", min_value=0)

    def test_negative_value(self):
        """Проверка отрицательного значения."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_positive(-5, "Тест", min_value=0)

    def test_max_value_exceeded(self):
        """Проверка превышения максимального значения."""
        with pytest.raises(ValidationError, match="должно быть меньше"):
            validate_positive(150, "Тест", min_value=0, max_value=100)


class TestValidateIbeamGeometry:
    """Тесты для валидации геометрии двутавра."""

    def test_valid_ibeam(self, sample_ibeam_params):
        """Проверка корректных параметров двутавра."""
        # Не должно вызвать исключение
        validate_ibeam_geometry(**sample_ibeam_params)

    def test_tw_greater_than_b(self, sample_ibeam_params):
        """Проверка: толщина стенки больше ширины полки."""
        params = sample_ibeam_params.copy()
        params["tw_mm"] = 150  # tw > b
        # Ошибка будет из validate_positive (tw > max_value=100)
        with pytest.raises(ValidationError):
            validate_ibeam_geometry(**params)

    def test_tf_too_large(self, sample_ibeam_params):
        """Проверка: толщина полки слишком большая."""
        params = sample_ibeam_params.copy()
        params["tf_mm"] = 150  # tf >= h/2
        # Ошибка будет из validate_positive (tf > max_value=100)
        with pytest.raises(ValidationError):
            validate_ibeam_geometry(**params)

    def test_two_flanges_exceed_height(self, sample_ibeam_params):
        """Проверка: две полки больше общей высоты."""
        params = sample_ibeam_params.copy()
        params["tf_mm"] = 120  # 2*120 = 240 > 200
        # Ошибка будет из validate_positive (tf > max_value=100)
        with pytest.raises(ValidationError):
            validate_ibeam_geometry(**params)


class TestValidateChannelGeometry:
    """Тесты для валидации геометрии швеллера."""

    def test_valid_channel(self, sample_ibeam_params):
        """Проверка корректных параметров швеллера."""
        # Швеллер использует ту же валидацию, что и двутавр
        validate_channel_geometry(**sample_ibeam_params)


class TestValidateRectTubeGeometry:
    """Тесты для валидации геометрии прямоугольной трубы."""

    def test_valid_rect_tube(self, sample_rect_tube_params):
        """Проверка корректных параметров прямоугольной трубы."""
        validate_rect_tube_geometry(**sample_rect_tube_params)

    def test_wall_too_thick_height(self, sample_rect_tube_params):
        """Проверка: стенка слишком толстая относительно высоты."""
        params = sample_rect_tube_params.copy()
        params["t_mm"] = 80  # 2*80 = 160 > 150
        with pytest.raises(ValidationError, match="Двойная толщина стенки.*должна быть меньше высоты"):
            validate_rect_tube_geometry(**params)

    def test_wall_too_thick_width(self, sample_rect_tube_params):
        """Проверка: стенка слишком толстая относительно ширины."""
        params = sample_rect_tube_params.copy()
        params["t_mm"] = 60  # 2*60 = 120 > 100
        with pytest.raises(ValidationError, match="Двойная толщина стенки.*должна быть меньше ширины"):
            validate_rect_tube_geometry(**params)


class TestValidateCircTubeGeometry:
    """Тесты для валидации геометрии круглой трубы."""

    def test_valid_circ_tube(self, sample_circ_tube_params):
        """Проверка корректных параметров круглой трубы."""
        validate_circ_tube_geometry(**sample_circ_tube_params)

    def test_wall_too_thick(self, sample_circ_tube_params):
        """Проверка: стенка слишком толстая (внутренний диаметр отрицательный)."""
        params = sample_circ_tube_params.copy()
        params["t_mm"] = 60  # 2*60 = 120 > 100
        with pytest.raises(ValidationError, match="Внутренний диаметр.*должен быть положительным"):
            validate_circ_tube_geometry(**params)


class TestValidateAngleGeometry:
    """Тесты для валидации геометрии уголка."""

    def test_valid_angle(self):
        """Проверка корректных параметров уголка."""
        validate_angle_geometry(b_mm=50, t_mm=5)

    def test_thickness_too_large(self):
        """Проверка: толщина больше ширины полки."""
        # Ошибка будет из validate_positive (t > max_value=50)
        with pytest.raises(ValidationError):
            validate_angle_geometry(b_mm=50, t_mm=60)


class TestValidateLoad:
    """Тесты для валидации нагрузок."""

    def test_valid_load(self):
        """Проверка корректной нагрузки."""
        validate_load(n_load_kn=100, load_type="Центральное сжатие")

    def test_negative_load(self):
        """Проверка отрицательной нагрузки."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_load(n_load_kn=-10, load_type="Центральное сжатие")


class TestValidateBendingLoad:
    """Тесты для валидации нагрузок при изгибе."""

    def test_valid_bending_loads(self):
        """Проверка корректных нагрузок при изгибе."""
        validate_bending_load(m_load_kNm=50, q_load_kn=20)

    def test_negative_moment(self):
        """Проверка отрицательного момента."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_bending_load(m_load_kNm=-10, q_load_kn=20)

    def test_negative_shear(self):
        """Проверка отрицательной поперечной силы."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_bending_load(m_load_kNm=50, q_load_kn=-5)


class TestValidateMaterial:
    """Тесты для валидации материала."""

    def test_valid_material(self, sample_material):
        """Проверка корректных параметров материала."""
        validate_material(**sample_material)

    def test_invalid_steel_grade(self, sample_material):
        """Проверка некорректной марки стали."""
        params = sample_material.copy()
        params["steel_grade"] = "C999"
        with pytest.raises(ValidationError, match="Неизвестная марка стали"):
            validate_material(**params)

    def test_invalid_ry(self, sample_material):
        """Проверка некорректного предела текучести."""
        params = sample_material.copy()
        params["ry_mpa"] = 50  # < 100
        with pytest.raises(ValidationError, match="Предел текучести"):
            validate_material(**params)

    def test_invalid_e(self, sample_material):
        """Проверка некорректного модуля упругости."""
        params = sample_material.copy()
        params["e_mpa"] = 50000  # < 100000
        with pytest.raises(ValidationError, match="Модуль упругости"):
            validate_material(**params)


class TestValidateGeometricLength:
    """Тесты для валидации геометрической длины."""

    def test_valid_geometric_length(self, sample_compression_params):
        """Проверка корректных параметров длины."""
        validate_geometric_length(**sample_compression_params)

    def test_negative_length(self):
        """Проверка отрицательной длины."""
        with pytest.raises(ValidationError, match="должно быть больше"):
            validate_geometric_length(l_geo_m=-1, mu=1.0)

    def test_invalid_mu_zero(self):
        """Проверка нулевого коэффициента."""
        with pytest.raises(ValidationError, match="Коэффициент расчетной длины"):
            validate_geometric_length(l_geo_m=3.0, mu=0)

    def test_invalid_mu_too_large(self):
        """Проверка слишком большого коэффициента."""
        with pytest.raises(ValidationError, match="Коэффициент расчетной длины"):
            validate_geometric_length(l_geo_m=3.0, mu=5.0)


class TestValidateAllInputs:
    """Тесты для комплексной валидации."""

    def test_valid_ibeam_tension(self, sample_ibeam_params, sample_material):
        """Проверка корректных входных данных для двутавра при растяжении."""
        result = validate_all_inputs(
            section_code="ibeam",
            geom_params=sample_ibeam_params,
            load_type="Центральное растяжение",
            loads={"n_load_kn": 100},
            material=sample_material
        )
        assert result is True

    def test_valid_ibeam_compression(self, sample_ibeam_params, sample_material, sample_compression_params):
        """Проверка корректных входных данных для двутавра при сжатии."""
        result = validate_all_inputs(
            section_code="ibeam",
            geom_params=sample_ibeam_params,
            load_type="Центральное сжатие",
            loads={"n_load_kn": 100},
            material=sample_material,
            compression_params=sample_compression_params
        )
        assert result is True

    def test_valid_bending(self, sample_ibeam_params, sample_material):
        """Проверка корректных входных данных для изгиба."""
        result = validate_all_inputs(
            section_code="ibeam",
            geom_params=sample_ibeam_params,
            load_type="Изгиб",
            loads={"m_load_kNm": 50, "q_load_kn": 20},
            material=sample_material
        )
        assert result is True

    def test_invalid_geometry_propagates(self, sample_material):
        """Проверка распространения ошибки валидации геометрии."""
        invalid_geom = {
            "h_mm": 200,
            "b_mm": 100,
            "tw_mm": 150,  # Некорректно: tw > b
            "tf_mm": 10
        }
        with pytest.raises(ValidationError):
            validate_all_inputs(
                section_code="ibeam",
                geom_params=invalid_geom,
                load_type="Центральное растяжение",
                loads={"n_load_kn": 100},
                material=sample_material
            )
