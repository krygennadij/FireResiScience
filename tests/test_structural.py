"""
Тесты для модуля прочностного расчета.
"""
import pytest
import math
from src.structural import (
    calc_c1_coefficient,
    calc_gamma_bending,
    calc_gamma_shear,
    calculate_geometry_ibeam,
    calculate_geometry_rect_tube,
    calculate_geometry_circ_tube,
    calculate_geometry_channel,
    get_phi_coeffs,
    calc_phi,
    calc_gamma_tension,
    calc_gamma_compression_stability
)


class TestC1Coefficient:
    """Тесты для расчета коэффициента c1."""

    def test_c1_with_normal_values(self):
        """Проверка расчета c1 с типовыми значениями."""
        af = 1000  # мм²
        aw = 2000  # мм²
        result = calc_c1_coefficient(af, aw)

        assert "value" in result
        assert "n" in result
        assert result["n"] == 0.5
        assert abs(result["value"] - 1.07) < 0.01

    def test_c1_with_zero_aw(self):
        """Проверка при нулевой площади стенки."""
        result = calc_c1_coefficient(1000, 0)
        assert result["value"] == 1.0
        assert result["n"] == 0

    def test_c1_bounds(self):
        """Проверка ограничений коэффициента c1."""
        # Малое n
        result = calc_c1_coefficient(100, 10000)
        assert result["value"] >= 1.0

        # Большое n
        result = calc_c1_coefficient(10000, 100)
        assert result["value"] <= 1.2


class TestGammaBending:
    """Тесты для расчета gamma при изгибе."""

    def test_gamma_bending_normal(self):
        """Проверка расчета gamma при изгибе."""
        m_load = 50  # кН·м
        w_section = 200000  # мм³
        ry = 245  # МПа
        gamma_c = 1.0
        c1 = 1.1

        gamma = calc_gamma_bending(m_load, w_section, ry, gamma_c, c1)
        # Функция работает напрямую с единицами без преобразования
        # gamma = M / (c1 * W * Ry)
        expected = m_load / (c1 * w_section * ry)
        assert abs(gamma - expected) < 1e-6

    def test_gamma_bending_zero_w(self):
        """Проверка при нулевом моменте сопротивления."""
        gamma = calc_gamma_bending(50, 0, 245, 1.0, 1.0)
        assert gamma == 999  # Защита от деления на ноль


class TestGammaShear:
    """Тесты для расчета gamma при сдвиге."""

    def test_gamma_shear_normal(self):
        """Проверка расчета gamma при сдвиге."""
        q_load = 20  # кН
        sx = 100000  # мм³
        ix = 10000000  # мм⁴
        tw = 6  # мм
        ry = 245  # МПа
        gamma_c = 1.0

        gamma = calc_gamma_shear(q_load, sx, ix, tw, ry, gamma_c)
        rs = 0.58 * ry
        # Функция работает напрямую с единицами без преобразования
        expected = (q_load * sx) / (ix * tw * rs * gamma_c)
        assert abs(gamma - expected) < 1e-6

    def test_gamma_shear_zero_ix(self):
        """Проверка при нулевом моменте инерции."""
        gamma = calc_gamma_shear(20, 100000, 0, 6, 245, 1.0)
        assert gamma == 999


class TestGeometryIbeam:
    """Тесты для расчета геометрии двутавра."""

    def test_ibeam_geometry(self, sample_ibeam_params):
        """Проверка расчета геометрии двутавра."""
        geom = calculate_geometry_ibeam(**sample_ibeam_params)

        assert "A" in geom
        assert "Ix" in geom
        assert "Iy" in geom
        assert "ix" in geom
        assert "iy" in geom
        assert "Wx" in geom
        assert "Sx" in geom
        assert "Af" in geom
        assert "Aw" in geom
        assert "tw" in geom
        assert geom["type"] == "ibeam"

        # Проверка положительности значений
        assert geom["A"] > 0
        assert geom["Ix"] > 0
        assert geom["Iy"] > 0
        assert geom["ix"] > 0
        assert geom["iy"] > 0

    def test_ibeam_area_calculation(self, sample_ibeam_params):
        """Проверка расчета площади двутавра."""
        geom = calculate_geometry_ibeam(**sample_ibeam_params)

        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]
        tf = sample_ibeam_params["tf_mm"]

        # A = 2*b*tf + (h-2*tf)*tw
        expected_area = 2 * b * tf + (h - 2 * tf) * tw
        assert abs(geom["A"] - expected_area) < 0.1


class TestGeometryRectTube:
    """Тесты для расчета геометрии прямоугольной трубы."""

    def test_rect_tube_geometry(self, sample_rect_tube_params):
        """Проверка расчета геометрии прямоугольной трубы."""
        geom = calculate_geometry_rect_tube(**sample_rect_tube_params)

        assert "A" in geom
        assert "Ix" in geom
        assert "Iy" in geom
        assert geom["type"] == "rect_tube"
        assert geom["A"] > 0

    def test_rect_tube_area(self, sample_rect_tube_params):
        """Проверка расчета площади прямоугольной трубы."""
        geom = calculate_geometry_rect_tube(**sample_rect_tube_params)

        h = sample_rect_tube_params["h_mm"]
        b = sample_rect_tube_params["b_mm"]
        t = sample_rect_tube_params["t_mm"]

        # A = h*b - (h-2t)*(b-2t)
        expected_area = h * b - (h - 2*t) * (b - 2*t)
        assert abs(geom["A"] - expected_area) < 0.1


class TestGeometryCircTube:
    """Тесты для расчета геометрии круглой трубы."""

    def test_circ_tube_geometry(self, sample_circ_tube_params):
        """Проверка расчета геометрии круглой трубы."""
        geom = calculate_geometry_circ_tube(**sample_circ_tube_params)

        assert "A" in geom
        assert "Ix" in geom
        assert "Iy" in geom
        assert geom["type"] == "circ_tube"
        assert geom["A"] > 0
        assert abs(geom["Ix"] - geom["Iy"]) < 0.01  # Для круглой трубы Ix = Iy

    def test_circ_tube_area(self, sample_circ_tube_params):
        """Проверка расчета площади круглой трубы."""
        geom = calculate_geometry_circ_tube(**sample_circ_tube_params)

        d = sample_circ_tube_params["d_mm"]
        t = sample_circ_tube_params["t_mm"]
        d_in = d - 2 * t

        # A = π*(d² - d_in²)/4
        expected_area = math.pi * (d**2 - d_in**2) / 4.0
        assert abs(geom["A"] - expected_area) < 0.1


class TestGeometryChannel:
    """Тесты для расчета геометрии швеллера."""

    def test_channel_geometry(self, sample_ibeam_params):
        """Проверка расчета геометрии швеллера."""
        geom = calculate_geometry_channel(**sample_ibeam_params)

        assert "A" in geom
        assert "Ix" in geom
        assert "Iy" in geom
        assert "Wx" in geom
        assert geom["type"] == "channel"
        assert geom["A"] > 0


class TestPhiCoefficients:
    """Тесты для получения коэффициентов φ."""

    def test_phi_coeffs_ibeam(self):
        """Проверка коэффициентов для двутавра."""
        alpha, beta, threshold, curve = get_phi_coeffs("ibeam")
        assert alpha == 0.04
        assert beta == 0.09
        assert threshold == 4.4
        assert curve == 'b'

    def test_phi_coeffs_channel(self):
        """Проверка коэффициентов для швеллера."""
        alpha, beta, threshold, curve = get_phi_coeffs("channel")
        assert alpha == 0.04
        assert beta == 0.14
        assert threshold == 5.8
        assert curve == 'c'

    def test_phi_coeffs_tube(self):
        """Проверка коэффициентов для труб."""
        alpha, beta, threshold, curve = get_phi_coeffs("circ_tube")
        assert alpha == 0.03
        assert beta == 0.06
        assert threshold == 3.8
        assert curve == 'a'


class TestCalcPhi:
    """Тесты для расчета коэффициента φ."""

    def test_phi_low_lambda(self):
        """Проверка при малой гибкости (λ < 0.6)."""
        phi, delta, lambda_bar, method = calc_phi(
            lambda_val=10,
            ry=245e6,  # Па
            e_modulus=2.06e11,  # Па
            alpha=0.04,
            beta=0.09,
            threshold=4.4,
            curve_code='b'
        )
        assert method == 'low_lambda'
        assert phi == 1.0

    def test_phi_high_lambda(self):
        """Проверка при высокой гибкости."""
        phi, delta, lambda_bar, method = calc_phi(
            lambda_val=300,
            ry=245e6,
            e_modulus=2.06e11,
            alpha=0.04,
            beta=0.09,
            threshold=4.4,
            curve_code='b'
        )
        assert method == 'high_lambda'
        assert phi > 0
        assert phi < 1.0

    def test_phi_standard_formula(self):
        """Проверка стандартной формулы."""
        phi, delta, lambda_bar, method = calc_phi(
            lambda_val=100,
            ry=245e6,
            e_modulus=2.06e11,
            alpha=0.04,
            beta=0.09,
            threshold=4.4,
            curve_code='b'
        )
        assert method == 'standard'
        assert 0 < phi < 1.0
        assert delta > 0


class TestGammaTension:
    """Тесты для расчета коэффициента при растяжении."""

    def test_gamma_tension_normal(self):
        """Проверка расчета gamma при растяжении."""
        n_load = 100  # кН
        area = 5000  # мм²
        ry = 245  # МПа
        gamma_c = 1.0

        gamma = calc_gamma_tension(n_load, area, ry, gamma_c)
        # Функция работает напрямую с единицами без преобразования
        expected = n_load / (area * ry * gamma_c)
        assert abs(gamma - expected) < 1e-6

    def test_gamma_tension_zero_area(self):
        """Проверка при нулевой площади."""
        gamma = calc_gamma_tension(100, 0, 245, 1.0)
        assert gamma == 0


class TestGammaCompressionStability:
    """Тесты для расчета коэффициента при сжатии с учетом устойчивости."""

    def test_compression_stability_normal(self):
        """Проверка расчета при сжатии."""
        result = calc_gamma_compression_stability(
            n_load=100,  # кН
            area=5000,  # мм²
            ry=245,  # МПа
            e_modulus=206000,  # МПа
            lef_x=3000,  # мм
            lef_y=3000,  # мм
            ix=80,  # мм
            iy=40,  # мм
            section_type="ibeam",
            gamma_c=1.0
        )

        assert "val" in result
        assert "phi" in result
        assert "lambda_bar" in result
        assert "lambda_val" in result
        assert "axis" in result
        assert result["val"] > 0
        assert 0 < result["phi"] <= 1.0

    def test_compression_determines_critical_axis(self):
        """Проверка определения критической оси."""
        # iy < ix, поэтому lambda_y > lambda_x -> ось y критическая
        result = calc_gamma_compression_stability(
            n_load=100,
            area=5000,
            ry=245,
            e_modulus=206000,
            lef_x=3000,
            lef_y=3000,
            ix=80,
            iy=40,  # Меньший радиус инерции
            section_type="ibeam",
            gamma_c=1.0
        )

        assert result["axis"] == "y"
        assert result["lambda_y"] > result["lambda_x"]

    def test_compression_zero_area(self):
        """Проверка при нулевой площади."""
        result = calc_gamma_compression_stability(
            n_load=100,
            area=0,
            ry=245,
            e_modulus=206000,
            lef_x=3000,
            lef_y=3000,
            ix=80,
            iy=40,
            section_type="ibeam",
            gamma_c=1.0
        )

        assert result["val"] == 0
        assert result["method"] == "error"
