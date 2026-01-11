"""
Модуль универсального селектора профилей для UI.
Упрощает выбор стандартных профилей из базы данных ГОСТ.
"""

import streamlit as st


def select_standard_profile(
    section_type,
    profile_data,
    label="Номер профиля",
    default_index=0,
    sort_key=None,
    checkbox_label="Стандартный профиль",
    checkbox_key=None
):
    """
    Универсальный селектор стандартных профилей с checkbox.

    Args:
        section_type (str): Тип сечения (для генерации ключей)
        profile_data (dict): Словарь с данными профилей
        label (str): Метка для selectbox
        default_index (int): Индекс профиля по умолчанию
        sort_key (callable, optional): Функция сортировки ключей профилей
        checkbox_label (str): Метка для checkbox
        checkbox_key (str, optional): Ключ для checkbox (генерируется автоматически если None)

    Returns:
        tuple: (geom_params dict or None, selected_profile_name or None)
               Если checkbox не выбран, возвращает (None, None)
    """
    if checkbox_key is None:
        checkbox_key = f"{section_type}_std_check"

    is_standard = st.checkbox(checkbox_label, value=True, key=checkbox_key)

    if is_standard and profile_data:
        # Сортировка профилей
        if sort_key:
            options = sorted(profile_data.keys(), key=sort_key)
        else:
            options = sorted(profile_data.keys())

        # Корректировка default_index если выходит за границы
        if default_index >= len(options):
            default_index = 0

        # Выбор профиля
        profile_name = st.selectbox(
            label,
            options,
            index=default_index,
            key=f"{section_type}_profile_select"
        )

        # Получение данных профиля
        profile_dict = profile_data[profile_name]

        # Формирование geom_params
        geom_params = {"number": profile_name}
        geom_params.update(profile_dict)

        return geom_params, profile_name

    return None, None


def get_manual_ibeam_params():
    """
    Возвращает параметры двутавра, введенные вручную.

    Returns:
        dict: Словарь с параметрами h_mm, b_mm, tw_mm, tf_mm
    """
    h = st.number_input(r"Высота $h$ (мм)", value=200.0, key="ibeam_h")
    b = st.number_input(r"Ширина полки $b$ (мм)", value=100.0, key="ibeam_b")
    tw = st.number_input(r"Толщина стенки $t_w$ (мм)", value=6.0, key="ibeam_tw")
    tf = st.number_input(r"Толщина полки $t_f$ (мм)", value=9.0, key="ibeam_tf")
    return {"h_mm": h, "b_mm": b, "tw_mm": tw, "tf_mm": tf}


def get_manual_channel_params():
    """
    Возвращает параметры швеллера, введенные вручную.

    Returns:
        dict: Словарь с параметрами h_mm, b_mm, tw_mm, tf_mm
    """
    h = st.number_input(r"Высота $h$ (мм)", value=200.0, key="channel_h")
    b = st.number_input(r"Ширина полки $b$ (мм)", value=80.0, key="channel_b")
    tw = st.number_input(r"Толщина стенки $t_w$ (мм)", value=6.0, key="channel_tw")
    tf = st.number_input(r"Толщина полки $t_f$ (мм)", value=9.0, key="channel_tf")
    return {"h_mm": h, "b_mm": b, "tw_mm": tw, "tf_mm": tf}


def get_manual_angle_params():
    """
    Возвращает параметры уголка, введенные вручную.

    Returns:
        dict: Словарь с параметрами b_mm, t_mm
    """
    b = st.number_input(r"Ширина полки $b$ (мм)", value=100.0, key="angle_b")
    t = st.number_input(r"Толщина $t$ (мм)", value=10.0, key="angle_t")
    return {"b_mm": b, "t_mm": t}


def get_manual_rect_tube_params():
    """
    Возвращает параметры прямоугольной трубы, введенные вручную.

    Returns:
        dict: Словарь с параметрами h_mm, b_mm, t_mm
    """
    h = st.number_input(r"Высота $h$ (мм)", value=100.0, key="rect_tube_h")
    b = st.number_input(r"Ширина $b$ (мм)", value=100.0, key="rect_tube_b")
    t = st.number_input(r"Толщина стенки $t$ (мм)", value=4.0, key="rect_tube_t")
    return {"h_mm": h, "b_mm": b, "t_mm": t}


def get_manual_circ_tube_params(key_suffix=""):
    """
    Возвращает параметры круглой трубы, введенные вручную.

    Args:
        key_suffix (str): Суффикс для уникальности ключей виджетов

    Returns:
        dict: Словарь с параметрами d_mm, t_mm
    """
    d = st.number_input(r"Диаметр $D$ (мм)", value=100.0, key=f"circ_tube_d{key_suffix}")
    t = st.number_input(r"Толщина стенки $t$ (мм)", value=4.0, key=f"circ_tube_t{key_suffix}")
    return {"d_mm": d, "t_mm": t}
