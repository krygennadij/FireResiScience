"""
Модуль кэширования для оптимизации производительности приложения.
Использует декораторы Streamlit @st.cache_data для кэширования результатов расчетов.
"""
import streamlit as st
from typing import Dict, Any


@st.cache_data(ttl=3600, show_spinner="Загрузка справочных данных...")
def load_reference_data():
    """
    Кэширует загрузку справочных данных ГОСТ (профили).
    TTL: 1 час (данные статичные, можно кэшировать долго).

    Returns:
        dict: Словарь со всеми справочными данными
    """
    from src import ibeam_data, channel_data, angle_data, pipe_data

    return {
        'ibeam': ibeam_data.IBEAM_DATA,
        'channel': channel_data.CHANNEL_DATA,
        'angle': angle_data.ANGLE_DATA,
        'pipe': pipe_data.PIPE_DATA
    }


def calculate_geometry_cached(section_code: str, geom_params: Dict[str, Any]) -> Dict[str, float]:
    """
    Кэширует расчет геометрических характеристик сечения.
    TTL: 30 минут.

    Args:
        section_code: Код типа сечения (ibeam, channel, angle, rect_tube, circ_tube)
        geom_params: Словарь с геометрическими параметрами

    Returns:
        dict: Геометрические характеристики в мм
    """
    from src import structural, ibeam_data, channel_data, angle_data, pipe_data

    if section_code == "ibeam":
        if "number" in geom_params:
            return ibeam_data.get_ibeam_props_mm(geom_params["number"])
        else:
            return structural.calculate_geometry_ibeam(**geom_params)

    elif section_code == "channel":
        if "number" in geom_params:
            return channel_data.get_channel_props_mm(geom_params["number"])

    elif section_code == "angle":
        if "number" in geom_params:
            props = angle_data.get_angle_props_mm(geom_params["number"])
            # Для уголков используем минимальный радиус инерции
            if "i_min" in props:
                props["iy"] = props["i_min"]
            return props

    elif section_code == "rect_tube":
        return structural.calculate_geometry_rect_tube(**geom_params)

    elif section_code == "circ_tube":
        if "number" in geom_params and pipe_data.PIPE_DATA:
            return pipe_data.get_pipe_props_mm(geom_params["number"])
        else:
            return structural.calculate_geometry_circ_tube(**geom_params)

    return {}


@st.cache_data(ttl=1800, show_spinner=False)
def calculate_critical_temp_cached(gamma_t: float, steel_grade: str) -> Dict[str, Any]:
    """
    Кэширует расчет критической температуры.
    TTL: 30 минут.

    Args:
        gamma_t: Коэффициент использования несущей способности
        steel_grade: Марка стали

    Returns:
        dict: Результат с критической температурой и trace данными
    """
    from src import data
    return data.get_critical_temp(gamma_t, steel_grade)


@st.cache_data(ttl=1800, show_spinner=False)
def calculate_fire_resistance_cached(
    Am_V: float,
    crit_temp: float,
    protection_type: str = "unprotected",
    prot_lambda: float = None,
    prot_thickness_mm: float = 0,
    time_step_sec: int = 10,
    max_time_min: int = 60
) -> Dict[str, Any]:
    """
    Кэширует теплотехнический расчет огнестойкости.
    TTL: 30 минут.

    Это самая ресурсоемкая операция (3600 итераций),
    поэтому кэширование дает максимальный эффект.

    Args:
        Am_V: Коэффициент сечения (1/м)
        crit_temp: Критическая температура (°C)
        protection_type: Тип защиты
        prot_lambda: Теплопроводность защиты
        prot_thickness_mm: Толщина защиты (мм)
        time_step_sec: Шаг времени (сек)
        max_time_min: Максимальное время расчета (мин)

    Returns:
        dict: Результаты с историей нагрева и пределом огнестойкости
    """
    from src import thermal

    return thermal.calculate_fire_resistance(
        Am_V=Am_V,
        crit_temp=crit_temp,
        protection_type=protection_type,
        prot_lambda=prot_lambda,
        prot_thickness_mm=prot_thickness_mm,
        time_step_sec=time_step_sec,
        max_time_min=max_time_min
    )


def calculate_heated_perimeter_cached(
    section_code: str,
    geom_params: Dict[str, Any],
    exposure_mode: str
) -> float:
    """
    Кэширует расчет обогреваемого периметра.
    TTL: 30 минут.

    Args:
        section_code: Код типа сечения
        geom_params: Геометрические параметры
        exposure_mode: Режим обогрева (3_sides или 4_sides)

    Returns:
        float: Обогреваемый периметр в мм
    """
    from src import thermal

    if section_code == "ibeam":
        return thermal.calc_heated_perimeter_ibeam(
            geom_params['h_mm'],
            geom_params['b_mm'],
            geom_params['tw_mm'],
            geom_params['tf_mm'],
            exposure=exposure_mode
        )
    elif section_code == "channel":
        return thermal.calc_heated_perimeter_channel(
            geom_params['h_mm'],
            geom_params['b_mm'],
            geom_params['tw_mm'],
            geom_params['tf_mm'],
            exposure=exposure_mode
        )
    elif section_code == "angle":
        b = geom_params.get('b_mm', 0)
        return 4 * b
    elif section_code == "rect_tube":
        return thermal.calc_heated_perimeter_rect_tube(
            geom_params['h_mm'],
            geom_params['b_mm'],
            exposure=exposure_mode
        )
    elif section_code == "circ_tube":
        return thermal.calc_heated_perimeter_circ_tube(
            geom_params['d_mm'],
            exposure=exposure_mode
        )

    return 0


def clear_all_caches():
    """
    Очищает все кэши приложения.
    Использовать при необходимости принудительного пересчета.
    """
    st.cache_data.clear()
