"""
Модуль валидации входных данных для расчета огнестойкости.
"""


class ValidationError(Exception):
    """Исключение для ошибок валидации."""
    pass


def validate_positive(value, name, min_value=0.0, max_value=None):
    """
    Проверяет, что значение положительное и в допустимых пределах.

    Args:
        value (float): Проверяемое значение
        name (str): Название параметра для сообщения об ошибке
        min_value (float): Минимальное допустимое значение (по умолчанию 0)
        max_value (float, optional): Максимальное допустимое значение

    Raises:
        ValidationError: Если значение не проходит валидацию
    """
    if value is None:
        raise ValidationError(f"{name}: значение не может быть пустым")

    if value <= min_value:
        raise ValidationError(f"{name}: значение должно быть больше {min_value}, получено {value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name}: значение должно быть меньше {max_value}, получено {value}")


def validate_ibeam_geometry(h_mm, b_mm, tw_mm, tf_mm):
    """
    Валидация геометрических параметров двутавра.

    Args:
        h_mm (float): Высота профиля (мм)
        b_mm (float): Ширина полки (мм)
        tw_mm (float): Толщина стенки (мм)
        tf_mm (float): Толщина полки (мм)

    Raises:
        ValidationError: Если параметры некорректны
    """
    # Проверка положительности
    validate_positive(h_mm, "Высота профиля h", min_value=0, max_value=2000)
    validate_positive(b_mm, "Ширина полки b", min_value=0, max_value=1000)
    validate_positive(tw_mm, "Толщина стенки tw", min_value=0, max_value=100)
    validate_positive(tf_mm, "Толщина полки tf", min_value=0, max_value=100)

    # Проверка физической корректности
    if tw_mm >= b_mm:
        raise ValidationError(f"Толщина стенки ({tw_mm} мм) должна быть меньше ширины полки ({b_mm} мм)")

    if tf_mm >= h_mm / 2:
        raise ValidationError(f"Толщина полки ({tf_mm} мм) должна быть меньше половины высоты ({h_mm/2} мм)")

    if 2 * tf_mm >= h_mm:
        raise ValidationError(f"Две полки ({2*tf_mm} мм) должны быть меньше общей высоты ({h_mm} мм)")


def validate_channel_geometry(h_mm, b_mm, tw_mm, tf_mm):
    """
    Валидация геометрических параметров швеллера.
    Аналогична валидации двутавра.
    """
    validate_ibeam_geometry(h_mm, b_mm, tw_mm, tf_mm)


def validate_rect_tube_geometry(h_mm, b_mm, t_mm):
    """
    Валидация геометрических параметров прямоугольной трубы.

    Args:
        h_mm (float): Высота (мм)
        b_mm (float): Ширина (мм)
        t_mm (float): Толщина стенки (мм)

    Raises:
        ValidationError: Если параметры некорректны
    """
    validate_positive(h_mm, "Высота h", min_value=0, max_value=2000)
    validate_positive(b_mm, "Ширина b", min_value=0, max_value=2000)
    validate_positive(t_mm, "Толщина стенки t", min_value=0, max_value=100)

    # Проверка, что стенки не слишком толстые
    if 2 * t_mm >= h_mm:
        raise ValidationError(f"Двойная толщина стенки ({2*t_mm} мм) должна быть меньше высоты ({h_mm} мм)")

    if 2 * t_mm >= b_mm:
        raise ValidationError(f"Двойная толщина стенки ({2*t_mm} мм) должна быть меньше ширины ({b_mm} мм)")


def validate_circ_tube_geometry(d_mm, t_mm):
    """
    Валидация геометрических параметров круглой трубы.

    Args:
        d_mm (float): Наружный диаметр (мм)
        t_mm (float): Толщина стенки (мм)

    Raises:
        ValidationError: Если параметры некорректны
    """
    validate_positive(d_mm, "Диаметр d", min_value=0, max_value=2000)
    validate_positive(t_mm, "Толщина стенки t", min_value=0, max_value=100)

    # Проверка, что внутренний диаметр положительный
    d_inner = d_mm - 2 * t_mm
    if d_inner <= 0:
        raise ValidationError(f"Внутренний диаметр ({d_inner} мм) должен быть положительным. "
                            f"Толщина стенки ({t_mm} мм) слишком велика для диаметра ({d_mm} мм)")


def validate_angle_geometry(b_mm, t_mm):
    """
    Валидация геометрических параметров равнополочного уголка.

    Args:
        b_mm (float): Ширина полки (мм)
        t_mm (float): Толщина (мм)

    Raises:
        ValidationError: Если параметры некорректны
    """
    validate_positive(b_mm, "Ширина полки b", min_value=0, max_value=500)
    validate_positive(t_mm, "Толщина t", min_value=0, max_value=50)

    if t_mm >= b_mm:
        raise ValidationError(f"Толщина ({t_mm} мм) должна быть меньше ширины полки ({b_mm} мм)")


def validate_load(n_load_kn, load_type):
    """
    Валидация нагрузки.

    Args:
        n_load_kn (float): Продольная нагрузка (кН)
        load_type (str): Тип нагружения

    Raises:
        ValidationError: Если нагрузка некорректна
    """
    validate_positive(n_load_kn, "Продольная нагрузка N", min_value=0, max_value=100000)


def validate_bending_load(m_load_kNm, q_load_kn):
    """
    Валидация нагрузок при изгибе.

    Args:
        m_load_kNm (float): Изгибающий момент (кН·м)
        q_load_kn (float): Поперечная сила (кН)

    Raises:
        ValidationError: Если нагрузки некорректны
    """
    validate_positive(m_load_kNm, "Изгибающий момент M", min_value=0, max_value=100000)
    validate_positive(q_load_kn, "Поперечная сила Q", min_value=0, max_value=100000)


def validate_material(steel_grade, ry_mpa, e_mpa):
    """
    Валидация материальных характеристик.

    Args:
        steel_grade (str): Марка стали
        ry_mpa (float): Предел текучести (МПа)
        e_mpa (float): Модуль упругости (МПа)

    Raises:
        ValidationError: Если характеристики некорректны
    """
    valid_grades = ["C235", "C245", "C255", "C345", "C345K", "C355", "C355-1", "C390"]
    if steel_grade not in valid_grades:
        raise ValidationError(f"Неизвестная марка стали: {steel_grade}")

    validate_positive(ry_mpa, "Предел текучести Ry", min_value=100, max_value=1000)
    validate_positive(e_mpa, "Модуль упругости E", min_value=100000, max_value=300000)


def validate_geometric_length(l_geo_m, mu):
    """
    Валидация геометрической длины и коэффициента расчетной длины.

    Args:
        l_geo_m (float): Геометрическая длина (м)
        mu (float): Коэффициент расчетной длины

    Raises:
        ValidationError: Если параметры некорректны
    """
    validate_positive(l_geo_m, "Геометрическая длина L", min_value=0, max_value=100)

    if mu <= 0 or mu > 3:
        raise ValidationError(f"Коэффициент расчетной длины μ должен быть в диапазоне (0, 3], получено {mu}")


def validate_all_inputs(section_code, geom_params, load_type, loads, material, compression_params=None):
    """
    Комплексная валидация всех входных данных.

    Args:
        section_code (str): Код типа сечения
        geom_params (dict): Геометрические параметры
        load_type (str): Тип нагружения
        loads (dict): Параметры нагрузки
        material (dict): Параметры материала
        compression_params (dict, optional): Параметры для сжатия

    Raises:
        ValidationError: Если любые данные некорректны

    Returns:
        bool: True если все валидации пройдены
    """
    try:
        # Валидация геометрии в зависимости от типа сечения
        if section_code == "ibeam" and "h_mm" in geom_params:
            validate_ibeam_geometry(
                geom_params["h_mm"],
                geom_params["b_mm"],
                geom_params["tw_mm"],
                geom_params["tf_mm"]
            )
        elif section_code == "channel" and "h_mm" in geom_params:
            validate_channel_geometry(
                geom_params["h_mm"],
                geom_params["b_mm"],
                geom_params["tw_mm"],
                geom_params["tf_mm"]
            )
        elif section_code == "rect_tube" and "h_mm" in geom_params:
            validate_rect_tube_geometry(
                geom_params["h_mm"],
                geom_params["b_mm"],
                geom_params["t_mm"]
            )
        elif section_code == "circ_tube" and "d_mm" in geom_params:
            validate_circ_tube_geometry(
                geom_params["d_mm"],
                geom_params["t_mm"]
            )
        elif section_code == "angle" and "b_mm" in geom_params:
            validate_angle_geometry(
                geom_params["b_mm"],
                geom_params["t_mm"]
            )

        # Валидация нагрузок
        if load_type == "Изгиб":
            validate_bending_load(loads["m_load_kNm"], loads["q_load_kn"])
        else:
            validate_load(loads["n_load_kn"], load_type)

        # Валидация материала
        validate_material(
            material["steel_grade"],
            material["ry_mpa"],
            material["e_mpa"]
        )

        # Валидация параметров сжатия
        if load_type == "Центральное сжатие" and compression_params:
            validate_geometric_length(
                compression_params["l_geo_m"],
                compression_params["mu"]
            )

        return True

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка валидации: {str(e)}")
