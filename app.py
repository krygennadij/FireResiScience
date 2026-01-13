import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# Try to import structural logic
try:
    from src import structural
    import src.data as data
    import src.thermal as thermal
    from src.ibeam_data import IBEAM_DATA, get_ibeam_props_mm
    from src.channel_data import CHANNEL_DATA, get_channel_props_mm
    import src.ibeam_data as ibeam_data
    import src.channel_data as channel_data
    import src.angle_data as angle_data
    import src.pipe_data as pipe_data
    from src.validation import ValidationError, validate_all_inputs
    from src.cache_helpers import (
        load_reference_data,
        calculate_critical_temp_cached,
        calculate_fire_resistance_cached,
        calculate_heated_perimeter_cached,
        clear_all_caches
    )
    from src.styles import get_custom_css
except ImportError as e:
    st.error(f"Ошибка импорта модулей: {e}")
    structural = None
    data = None
    thermal = None
    ibeam_data = None
    channel_data = None
    ValidationError = None
    validate_all_inputs = None

def main():
    st.set_page_config(
        page_title="Расчет огнестойкости | FireResiScience",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🔥 Расчёт предела огнестойкости стальных строительных конструкций")

    # Применяем пользовательские CSS-стили
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # SIDEBAR: INPUTS
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.header("🔥 FireResiScience")
        st.caption("Расчет огнестойкости стальных конструкций")
        st.divider()

    st.sidebar.header("📋 Исходные данные")

    # -------------------------------------------------------------------------
    # 1. Geometry (Moved up)
    # -------------------------------------------------------------------------
    with st.sidebar.expander("Параметры сечения", expanded=True):
        # Section Type Map (UI Name -> Code)
        section_map = {
            "Двутавр": "ibeam",
            "Швеллер": "channel",
            "Уголок": "angle",
            "Труба прямоугольная": "rect_tube",
            "Труба круглая": "circ_tube"
        }

        # Инициализация в session_state если еще нет
        if 'section_type' not in st.session_state:
            st.session_state.section_type = "Двутавр"

        st.markdown("**Тип сечения:**")
        section_type_ui = st.pills(
            "section_type_selector",
            options=list(section_map.keys()),
            default=st.session_state.section_type,
            label_visibility="collapsed",
            help="Выберите тип поперечного сечения конструкции"
        )

        # Обновляем session_state
        if section_type_ui:
            st.session_state.section_type = section_type_ui
        else:
            section_type_ui = st.session_state.section_type

        section_code = section_map[section_type_ui]

        # Init variables
        geom_params = {}
        is_standard_ibeam = False

        if section_type_ui == "Двутавр":
            section_code = "ibeam"
            is_standard_ibeam = st.checkbox("Стандартный профиль", value=True)

            if is_standard_ibeam and ibeam_data:
                # Sort numbers numerically
                opts = sorted(ibeam_data.IBEAM_DATA.keys(), key=lambda x: int(x))
                def_idx = 5 if len(opts) > 5 else 0
                ibeam_num = st.selectbox("Номер профиля", opts, index=def_idx, key="ibeam_profile_select")

                d = ibeam_data.IBEAM_DATA[ibeam_num]
                # st.caption removed
                geom_params = {"number": ibeam_num}
                geom_params.update({"h_mm": d['h'], "b_mm": d['b'], "tw_mm": d['s'], "tf_mm": d['t']})

            else:
                h = st.number_input(r"Высота $h$ (мм)", value=200.0, key="ibeam_h")
                b = st.number_input(r"Ширина полки $b$ (мм)", value=100.0, key="ibeam_b")
                tw = st.number_input(r"Толщина стенки $t_w$ (мм)", value=6.0, key="ibeam_tw")
                tf = st.number_input(r"Толщина полки $t_f$ (мм)", value=9.0, key="ibeam_tf")
                geom_params = {"h_mm": h, "b_mm": b, "tw_mm": tw, "tf_mm": tf}

        elif section_code == "channel":
            is_std_channel = st.checkbox("Стандартный профиль", value=True, key="channel_std_check")
            if is_std_channel and CHANNEL_DATA:
                opts = sorted(CHANNEL_DATA.keys(), key=lambda x: float(x.replace('У','').replace('U','')) if x.replace('У','').replace('U','').replace('.','').isdigit() else 0)
                def_idx = 8 if len(opts) > 8 else 0
                chan_num = st.selectbox("Номер профиля (ГОСТ 8240-97)", opts, index=def_idx, key="channel_profile_select")
                d_chan = CHANNEL_DATA[chan_num]
                # st.caption removed
                geom_params = {"number": chan_num}
                geom_params.update({"h_mm": d_chan['h'], "b_mm": d_chan['b'], "tw_mm": d_chan['s'], "tf_mm": d_chan['t']})
            else:
                h = st.number_input(r"Высота $h$ (мм)", value=200.0, key="channel_h")
                b = st.number_input(r"Ширина полки $b$ (мм)", value=80.0, key="channel_b")
                tw = st.number_input(r"Толщина стенки $t_w$ (мм)", value=6.0, key="channel_tw")
                tf = st.number_input(r"Толщина полки $t_f$ (мм)", value=9.0, key="channel_tf")
                geom_params = {"h_mm": h, "b_mm": b, "tw_mm": tw, "tf_mm": tf}

        elif section_code == "angle":
            is_std_angle = st.checkbox("Стандартный профиль", value=True, key="angle_std_check")
            if is_std_angle and angle_data.ANGLE_DATA:
                # Custom sort for Angle keys
                def sort_key(k):
                    try:
                        k = k.replace("L", "")
                        parts = k.split("x")
                        return float(parts[0]), float(parts[1])
                    except:
                        return 0, 0

                opts = sorted(angle_data.ANGLE_DATA.keys(), key=sort_key)
                def_idx = 0
                for i, o in enumerate(opts):
                    if "L75" in o:
                        def_idx = i
                        break

                angle_name = st.selectbox("Номер уголка (ГОСТ 8509-93)", opts, index=def_idx, key="angle_profile_select")
                d_ang = angle_data.ANGLE_DATA[angle_name]
                # st.caption removed
                geom_params = {"number": angle_name}
                geom_params.update({"b_mm": d_ang['b'], "t_mm": d_ang['t']})
            else:
                b = st.number_input(r"Ширина полки $b$ (мм)", value=100.0, key="angle_b")
                t = st.number_input(r"Толщина $t$ (мм)", value=10.0, key="angle_t")
                geom_params = {"b_mm": b, "t_mm": t}

        elif section_code == "rect_tube":
            is_std_rect = st.checkbox("Стандартный профиль", value=False, disabled=True, help="База данных профилей пока не подключена", key="rect_std_check")
            if is_std_rect:
                st.info("Выбор из сортамента в разработке.")
            # Manual inputs always shown for now or if unchecked
            h = st.number_input(r"Высота $h$ (мм)", value=100.0, key="rect_tube_h")
            b = st.number_input(r"Ширина $b$ (мм)", value=100.0, key="rect_tube_b")
            t = st.number_input(r"Толщина стенки $t$ (мм)", value=4.0, key="rect_tube_t")
            geom_params = {"h_mm": h, "b_mm": b, "t_mm": t}

        elif section_code == "circ_tube":
            # Pipe Data GOST 8732
            if pipe_data.PIPE_DATA:
                is_std_pipe = st.checkbox("Стандартный профиль", value=True)
                if is_std_pipe:
                    # Sort by D then T
                    def pipe_sort(k):
                        # k="108x4"
                        try:
                            parts = k.split('x')
                            return float(parts[0]), float(parts[1])
                        except:
                            return 0,0

                    opts = sorted(pipe_data.PIPE_DATA.keys(), key=pipe_sort)
                    def_idx = 0
                    # Try default near 108
                    for i,o in enumerate(opts):
                        if o.startswith("108"):
                            def_idx = i
                            break

                    pipe_name = st.selectbox("Профиль трубы (dx t)", opts, index=def_idx, key="circ_tube_profile_select")
                    d_pipe = pipe_data.PIPE_DATA[pipe_name]
                # st.caption removed
                    geom_params = {"number": pipe_name, "d_mm": d_pipe['d'], "t_mm": d_pipe['t']}

                else:
                    d = st.number_input(r"Диаметр $D$ (мм)", value=100.0, key="circ_tube_d_custom")
                    t = st.number_input(r"Толщина стенки $t$ (мм)", value=4.0, key="circ_tube_t_custom")
                    geom_params = {"d_mm": d, "t_mm": t}
            else:
                d = st.number_input(r"Диаметр $D$ (мм)", value=100.0, key="circ_tube_d_nostd")
                t = st.number_input(r"Толщина стенки $t$ (мм)", value=4.0, key="circ_tube_t_nostd")
                geom_params = {"d_mm": d, "t_mm": t}
        
        # Placeholder removed

    # 2. Material
    with st.sidebar.expander("Материал", expanded=True):
        steel_grade = st.selectbox("Марка стали", ["C235", "C245", "C255", "C345", "C345K", "C355", "C355-1", "C390"], key="steel_grade_select")

        # Determine determining thickness (usually flange thickness tf or wall t)
        thickness_for_ry = 10.0 # default
        if "tf_mm" in geom_params:
            thickness_for_ry = geom_params["tf_mm"]
        elif "t_mm" in geom_params:
            thickness_for_ry = geom_params["t_mm"]

        ryn_calc = data.get_ryn(steel_grade, thickness_for_ry)

        st.caption(f"Толщина проката (полки): {thickness_for_ry} мм")

        # Let user override or see the value
        # Let user override or see the value (Normative Ryn)
        # Use dynamic key so it resets when grade/thickness changes
        ryn_val = st.number_input(r"$R_{yn}$ (МПа)", value=float(ryn_calc), disabled=False, key=f"ryn_input_{steel_grade}_{thickness_for_ry}")
        e_modulus = st.number_input(r"$E$ (МПа)", value=206000.0, key="e_modulus_input")

    # 3. Loads
    with st.sidebar.expander("Нагрузки", expanded=True):
        load_options = ["Центральное сжатие", "Центральное растяжение", "Изгиб"]

        # Инициализация в session_state если еще нет
        if 'load_type' not in st.session_state:
            st.session_state.load_type = "Центральное сжатие"

        load_type = st.pills(
            "load_type_selector",
            options=load_options,
            default=st.session_state.load_type,
            label_visibility="collapsed",
            help="Выберите характер работы конструкции"
        )

        # Обновляем session_state
        if load_type:
            st.session_state.load_type = load_type
        else:
            load_type = st.session_state.load_type

        n_load_kn = 0
        m_load_kNm = 0
        q_load_kn = 0
        lef_x = 0
        lef_y = 0

        if load_type == "Изгиб":
            m_load_kNm = st.number_input(r"Изгибающий момент $M$ (кН·м)", value=20.0, key="m_load")
            q_load_kn = st.number_input(r"Поперечная сила $Q$ (кН)", value=50.0, key="q_load")
        else:
            n_load_kn = st.number_input(r"Продольная сила $N$ (кН)", value=500.0, key="n_load")
            if load_type == "Центральное сжатие":
                # Geometric Length
                l_geo_m = st.number_input(r"Геометрическая длина $L$ (м)", value=3.0, key="l_geo")

                # Calculation Scheme Selection
                schemes = {
                    "Сх. 5 (Консоль)": 2.0,
                    "Сх. 6 (Шарнир-Шарнир)": 1.0,
                    "Сх. 7 (Заделка-Заделка)": 0.5,
                    "Сх. 8 (Заделка-Шарнир)": 0.7,
                    "Другое (вручную)": 0.0
                }

                scheme_ui = st.selectbox("Расчетная схема (Табл. А.4)", list(schemes.keys()), index=1, key="scheme_select") # Default scheme 6 (1.0)

                if scheme_ui == "Другое (вручную)":
                    mu_val = st.number_input(r"Коэф. расчетной длины $\mu$", value=1.0, key="mu_custom")
                else:
                    mu_val = schemes[scheme_ui]
                st.caption(f"Коэффициент расчетной длины $\mu = {mu_val}$")

                # Calculate Effective Length (Same for X and Y as requested)
                mu_x = mu_val
                mu_y = mu_val
                lef_x = l_geo_m * mu_val
                lef_y = l_geo_m * mu_val
                lef_display = lef_x # Only need one variable for display

                # Store for display later (optional, separate from lef_x passed to logic)
                # We will use these variables in step 3 for display

    # 4. Fire Parameters
    with st.sidebar.expander("Параметры пожара", expanded=True):
        # Heating Schemes
        if "heating_scheme" not in st.session_state:
            st.session_state.heating_scheme = "4_sides"

        # Helper to display fixed height image
        def get_img_html(path, height=100):
            try:
                import base64
                with open(path, "rb") as f:
                    data = f.read()
                    enc = base64.b64encode(data).decode()
                ext = "svg+xml" if path.endswith(".svg") else "png"
                return f'<img src="data:image/{ext};base64,{enc}" style="height: {height}px; object-fit: contain; width: 100%;">'
            except Exception:
                return "Image not found"

        # Determine paths based on section type
        img_4 = "assets/I_4_sides.svg"
        img_3 = "assets/I_3_sides.png"

        if section_code == "channel":
            img_4 = "assets/[_4_sides.svg"
            img_3 = "assets/[_3_sides.svg"
        elif section_code == "angle":
            img_4 = "assets/L_4_sides.svg"
            img_3 = "assets/L_3_sides.svg"
        elif section_code == "rect_tube":
            img_4 = "assets/[]_4_sides.svg"
            img_3 = "assets/[]_3_sides.svg"

        if section_code == "circ_tube":
            st.session_state.heating_scheme = "4_sides"
            st.markdown(get_img_html("assets/o_3_sides.svg", 100), unsafe_allow_html=True)
            st.caption("⭕ Обогрев со всех сторон (круглая труба)")
        else:
            # Кликабельные изображения схем обогрева
            col_img1, col_img2 = st.columns(2)

            # Получаем текущую схему обогрева
            current_scheme = st.session_state.get('heating_scheme', '4_sides')

            with col_img1:
                # Стиль рамки в зависимости от выбора
                border_style = "border: 3px solid #FF4B4B;" if current_scheme == "3_sides" else "border: 2px solid #e0e0e0;"
                st.markdown(f'<div style="{border_style} border-radius: 8px; padding: 5px;">{get_img_html(img_3, 90)}</div>', unsafe_allow_html=True)
                if st.button("3 стороны", key="btn_3_sides", use_container_width=True, help="Частичный обогрев"):
                    st.session_state.heating_scheme = "3_sides"
                    st.rerun()

            with col_img2:
                # Стиль рамки в зависимости от выбора
                border_style = "border: 3px solid #FF4B4B;" if current_scheme == "4_sides" else "border: 2px solid #e0e0e0;"
                st.markdown(f'<div style="{border_style} border-radius: 8px; padding: 5px;">{get_img_html(img_4, 90)}</div>', unsafe_allow_html=True)
                if st.button("4 стороны", key="btn_4_sides", use_container_width=True, help="Обогрев со всех сторон"):
                    st.session_state.heating_scheme = "4_sides"
                    st.rerun()

        # Apply state
        exposure_mode = st.session_state.heating_scheme
            
        max_time_min = 60 # Fixed time as requested
        dt_step = 10 

    # -------------------------------------------------------------------------
    # MAIN AREA: RESULTS
    # -------------------------------------------------------------------------
    
    if structural is None:
        st.error("Ошибка: Модули расчета не найдены.")
        return

    # Валидация входных данных
    if validate_all_inputs is not None:
        try:
            # Подготовка данных для валидации
            loads_dict = {}
            if load_type == "Изгиб":
                loads_dict = {"m_load_kNm": m_load_kNm, "q_load_kn": q_load_kn}
            else:
                loads_dict = {"n_load_kn": n_load_kn}

            material_dict = {
                "steel_grade": steel_grade,
                "ry_mpa": ryn_val,
                "e_mpa": e_modulus
            }

            compression_dict = None
            if load_type == "Центральное сжатие":
                compression_dict = {"l_geo_m": l_geo_m, "mu": mu_val}

            # Вызов валидации
            validate_all_inputs(
                section_code=section_code,
                geom_params=geom_params,
                load_type=load_type,
                loads=loads_dict,
                material=material_dict,
                compression_params=compression_dict
            )
        except ValidationError as ve:
            st.error(f"❌ Ошибка валидации данных: {ve}")
            st.toast(f"⚠️ {str(ve)[:100]}", icon="⚠️")
            return
        except Exception as e:
            st.warning(f"⚠️ Не удалось выполнить валидацию: {e}")

    # A. Calculate Geometry
    props_mm = {}
    try:
        if section_code == "ibeam":
            if is_standard_ibeam and ibeam_data:
                props_mm = ibeam_data.get_ibeam_props_mm(geom_params["number"])
            else:
                props_mm = structural.calculate_geometry_ibeam(**geom_params)
        elif section_code == "channel":
             if "number" in geom_params:
                # We already loaded it inside the sidebar logic block into props_mm? 
                # No, geom_params has "number". We need to call get_channel_props_mm.
                props_mm = channel_data.get_channel_props_mm(geom_params["number"])
             else:
                props_mm = structural.calculate_geometry_channel(**geom_params)
        elif section_code == "angle":
            if "number" in geom_params:
                props_mm = angle_data.get_angle_props_mm(geom_params["number"])
                # Important: For Angle stability, usually min radius of gyration is critical.
                # Standard check uses max lambda = lef / i_min. 
                # Our structural logic uses lambda_y = lef / iy. 
                # So we map iy -> i_min to ensure stability check uses the worst case.
                if "i_min" in props_mm:
                    props_mm["iy"] = props_mm["i_min"]
            else:
                pass
        elif section_code == "rect_tube":
            props_mm = structural.calculate_geometry_rect_tube(**geom_params)
        elif section_code == "circ_tube":
            if "number" in geom_params and pipe_data.PIPE_DATA:
                props_mm = pipe_data.get_pipe_props_mm(geom_params["number"])
            else:
                props_mm = structural.calculate_geometry_circ_tube(**geom_params)
            # Circular tube usually 4 sides only effectively
            if exposure_mode == "3_sides":
                st.sidebar.warning("Для круглой трубы частичный обогрев рассчитывается как полный (П = pi*d).")
                exposure_mode = "4_sides"
                
    except Exception as e:
        st.error(f"Ошибка геометрии: {e}")
        return

    # Helper: Convert to SI (m, m2, m3, m4) from mm
    def scale_prop(val, power):
        return val * (10**(-3 * power))

    props_si = props_mm.copy()
    props_si['A'] = scale_prop(props_mm['A'], 2)   # m2
    props_si['Ix'] = scale_prop(props_mm['Ix'], 4) # m4
    props_si['Iy'] = scale_prop(props_mm['Iy'], 4) # m4
    props_si['ix'] = scale_prop(props_mm['ix'], 1) # m

    # Update Geometry Info in Sidebar
    # Update Geometry Info in Sidebar - Removed per user request
    # if geom_info_placeholder: ...
    props_si['iy'] = scale_prop(props_mm['iy'], 1) # m
    if 'Wx' in props_mm: props_si['Wx'] = scale_prop(props_mm['Wx'], 3) # m3
    if 'Sx' in props_mm: props_si['Sx'] = scale_prop(props_mm['Sx'], 3) # m3
    if 'tum' in props_mm: pass # unused
    
    # We also need primitives like tw, tf in meters for Shear calc (tw)
    if 'tw' in props_mm: props_si['tw'] = scale_prop(props_mm['tw'], 1)
    
    # Helper: Custom Scientific Notation for LaTeX (e.g. 2.35 * 10^8)
    def fmt_latex_ryn_mpa(val_pa):
        """
        Formats Pascal value as MPa * 10^6.
        Example: 245000000 -> 245 \\cdot 10^6
        """
        if val_pa == 0: return "0"
        val_mpa = val_pa / 1e6
        return fr"{val_mpa:.0f} \cdot 10^{{6}}"

    def fmt_latex_sci(val: float, precision=2) -> str:
        if val == 0: return "0"
        s = "{:.{}e}".format(val, precision)
        base, exponent = s.split("e")
        if not exponent: return base
        exp_int = int(exponent)
        return fr"{base} \cdot 10^{{{exp_int}}}"

    # --- PERFORM ALL CALCULATIONS FIRST ---
    
    # 1. Structural
    n_newton = abs(n_load_kn) * 1000.0
    m_newton_m = abs(m_load_kNm) * 1000.0
    q_newton = abs(q_load_kn) * 1000.0

    # Use User Input from Sidebar (which defaults to Normative Ryn) 
    # for all calculations in Fire Design context.
    ryn_pascal = ryn_val * 1e6
    e_pascal = e_modulus * 1e6
    
    # --- Ryn Logic ---
    # We now use 'ryn_val' from sidebar directly.
    # It defaults to data.get_ryn(...) based on thickness.
    # No need to re-fetch unless we wanted to ignore user override.
    # We respect user override.


    gamma_t = 0
    gamma_c = 1.0 
    
    gamma_t_bending = 0
    gamma_t_shear = 0
    
    res_compression = {} 

    calc_error = None
    
    
    # Calculate critical temperature
    # Note: calculate_critical_temp uses props_si['A']
    # Check if A exists in props_si
    if "A" not in props_si and "A" in props_mm:
         props_si["A"] = props_mm["A"] * 1e-6 # Manual fallback if not already set
    
    try:
        if load_type == "Центральное растяжение":
            # Use Ryn (Normative) for Tensile Fire Resistance check?
            # User implies check Ryn.
            gamma_t = structural.calc_gamma_tension(n_newton, props_si["A"], ryn_pascal)
        elif load_type == "Центральное сжатие":
            # 1. Calc Phi using Ryn (User Input / Normative for Fire)
            # Note: Standard uses Ry. Fire Design often uses Normative. User Sidebar is labeled Ryn.
            res_compression = structural.calc_gamma_compression_stability(
                n_newton, props_si["A"], ryn_pascal, e_pascal, 
                lef_x, lef_y, props_si["ix"], props_si["iy"], section_code
            )
            gamma_t = res_compression["val"] # This now uses Ryn in denominator automatically via structural calc
        elif load_type == "Изгиб":
            c1_val = 1.0
            if section_code == "ibeam":
                af = props_mm.get("Af", 0)
                aw = props_mm.get("Aw", 1)
                c1_res = structural.calc_c1_coefficient(af, aw)
                c1_val = c1_res["value"]
            elif section_code == "channel":
                af = props_mm.get("Af", 0)
                aw = props_mm.get("Aw", 1)
                c1_res = structural.calc_c1_coefficient(af, aw)
                c1_val = c1_res["value"]
            
            
            # Use Ryn for Bending Resistance
            gamma_t_bending = structural.calc_gamma_bending(
                m_newton_m, props_si.get("Wx", 0), ryn_pascal, c1=c1_val
            )
            gamma_t_shear = structural.calc_gamma_shear(
                 q_newton, props_si.get("Sx", 0), props_si.get("Ix", 1), props_si.get("tw", 0), ryn_pascal
             )
            gamma_t = max(gamma_t_bending, gamma_t_shear)
    except Exception as e:
        calc_error = str(e)

    # 2. Critical Temperature
    crit_result = data.get_critical_temp(gamma_t, steel_grade)
    crit_temp = crit_result["value"]
    
    # 3. Thermal / Fire Resistance
    # Calculate Perimeter based on exposure
    perimeter_mm = 0
    if section_code == "ibeam":
        perimeter_mm = thermal.calc_heated_perimeter_ibeam(
            geom_params['h_mm'], geom_params['b_mm'], geom_params['tw_mm'], geom_params['tf_mm'], 
            exposure=exposure_mode
        )
    elif section_code == "channel":
        perimeter_mm = thermal.calc_heated_perimeter_channel(
            geom_params['h_mm'], geom_params['b_mm'], geom_params['tw_mm'], geom_params['tf_mm'],
            exposure=exposure_mode
        )
    elif section_code == "angle":
        # Formula: A/(2b1+2b2). For equal angle: P = 2b + 2b = 4b.
        b = geom_params.get('b_mm', 0)
        perimeter_mm = 4 * b
    elif section_code == "rect_tube":
        perimeter_mm = thermal.calc_heated_perimeter_rect_tube(
            geom_params['h_mm'], geom_params['b_mm'], 
            exposure=exposure_mode
        )
    elif section_code == "circ_tube":
        perimeter_mm = thermal.calc_heated_perimeter_circ_tube(geom_params['d_mm'], exposure=exposure_mode)
        
    calc_Am_V = 0
    delta_np_mm = 0
    if perimeter_mm > 0 and props_mm['A'] > 0:
        # A/P (mm2 / mm = mm) -> Reduced Thickness delta_np
        delta_np_mm = props_mm['A'] / perimeter_mm 
        
        # Section factor Am/V (1/m) = P/A * 1000
        # Or 1000 / delta_np_mm
        calc_Am_V = 1000.0 / delta_np_mm 
    
    fire_res_result = None
    if calc_Am_V > 0:
            fire_res_result = thermal.calculate_fire_resistance(
                Am_V=calc_Am_V,
                crit_temp=crit_temp,
                protection_type="unprotected",
                prot_lambda=None,
                prot_thickness_mm=0,
                time_step_sec=dt_step,
                max_time_min=max_time_min
            )

    # --- UI LAYOUT ---
    
    if calc_error:
        st.error(f"Ошибка расчета: {calc_error}")
        return

    # TABS
    # TABS
    tab_calc, tab_report, tab_validation = st.tabs(["📝 Расчет", "📄 Отчет", "🔬 Валидация"])
    
    # --- TAB 1: DETAILED CALCULATION ---
    with tab_calc:
        # Ключевые результаты в метриках (сверху)
        st.subheader("🎯 Основные результаты расчета")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.metric(
                label="Коэффициент γT",
                value=f"{gamma_t:.4f}",
                help="Коэффициент использования несущей способности сечения при нормальной температуре"
            )

        with col_m2:
            st.metric(
                label="Критическая температура",
                value=f"{crit_temp:.0f} °C",
                help="Температура, при которой конструкция теряет несущую способность"
            )

        with col_m3:
            if fire_res_result:
                fire_res_time = fire_res_result['raw_time']
                st.metric(
                    label="Фактический предел",
                    value=f"R{int(fire_res_time)}",
                    delta=f"{fire_res_time:.1f} мин",
                    help="Фактический предел огнестойкости конструкции"
                )

        with col_m4:
            if fire_res_result:
                st.metric(
                    label="Приведенная толщина",
                    value=f"{delta_np_mm:.2f} мм",
                    help="Приведенная толщина металла (δnp = A/П)"
                )

        st.divider()

        # 1. Structural Details
        with st.expander("1. Статическая (прочностная) задача", expanded=False):
            if load_type == "Центральное растяжение":
                 tex_eq = r"\gamma_T = \frac{N}{A \cdot R_{yn} \cdot \gamma_c}"
                 tex_subst = fr"\frac{{{n_newton:.0f}}}{{{fmt_latex_sci(props_si['A'])}\cdot {fmt_latex_ryn_mpa(ryn_pascal)} \cdot {gamma_c}}}"
                 st.latex(fr"{tex_eq} = {tex_subst} = \mathbf{{{gamma_t:.4f}}}")
                 
            elif load_type == "Центральное сжатие":
                # Reuse the detailed logic from previous step
                phi_val = res_compression["phi"]
                lambda_bar = res_compression["lambda_bar"]
                
                # Display Effective Length Calculation
                # Reordering per request: Remove "A. ..." header. 
                # Move "Determination of calculated flexibility..." to here.
                
                st.markdown(r"Определение расчетной гибкости стержневой конструкции")
                
                # Single Lef display
                st.latex(fr"L_{{ef}} = \mu \cdot L = {mu_val} \cdot {l_geo_m} = {lef_display:.2f} \text{{ м}} = {lef_display*1000:.0f} \text{{ мм}}")
                
                # Lambda X and Y
                st.markdown(r"Гибкость относительно главных осей:")
                st.latex(fr"\lambda_x = \frac{{L_{{ef}}}}{{i_x}} = \frac{{{lef_display*1000:.0f}}}{{{props_mm['ix']:.1f}}} = \mathbf{{{res_compression['lambda_x']:.1f}}}")
                st.latex(fr"\lambda_y = \frac{{L_{{ef}}}}{{i_y}} = \frac{{{lef_display*1000:.0f}}}{{{props_mm['iy']:.1f}}} = \mathbf{{{res_compression['lambda_y']:.1f}}}")

                # Max Lambda
                st.latex(fr"\lambda_{{max}} = \max(\lambda_x, \lambda_y) = \max({res_compression['lambda_x']:.1f}, {res_compression['lambda_y']:.1f}) = \mathbf{{{res_compression['lambda_val']:.1f}}}")
                
                 # Continue with B. Conditional Flexibility (renamed to V. etc)
                st.markdown(r"Определение условной гибкости стержневой конструкции")
                # lambda_bar = lambda_max * sqrt(Ryn/E)
                st.latex(fr"\bar{{\lambda}} = \lambda_{{max}} \sqrt{{\frac{{R_{{yn}}}}{{E}}}} = {res_compression['lambda_val']:.1f} \cdot \sqrt{{\frac{{{fmt_latex_ryn_mpa(ryn_pascal)}}}{{{fmt_latex_sci(e_pascal)}}}}} = \mathbf{{{lambda_bar:.3f}}}")
                
                st.markdown(r"Определение коэффициента устойчивости при центральном сжатии")
                
                phi_method = res_compression.get("method", "standard")
                threshold = res_compression.get("threshold", 0)
                curve_code = res_compression.get("curve_code", "?")
                
                if phi_method == "low_lambda":
                    st.write(f"Условие: $\overline{{\lambda}} < 0.6$ (для кривой '{curve_code}')")
                    st.latex(r"\Rightarrow \varphi = 1.0")
                elif phi_method == "high_lambda":
                    st.markdown(fr"Проверка условия (СП 16.13330):")
                    st.latex(fr"\bar{{\lambda}} = {lambda_bar:.3f} > {threshold} \quad (\text{{для типа кривой }} '{curve_code}')")
                    st.write(r"Т.к. условие выполняется, расчет $\varphi$ ведется по формуле:")
                    st.latex(fr"\varphi = \frac{{7.6}}{{\bar{{\lambda}}^2}} = \frac{{7.6}}{{{lambda_bar:.3f}^2}} = \mathbf{{{phi_val:.3f}}}")
                else: # standard
                    delta = res_compression["delta"]
                    alpha = res_compression["alpha"]
                    st.write(fr"Расчет по формуле (кривая '{curve_code}', $\alpha={alpha}$, $\beta={res_compression['beta']}$)")
                    st.latex(fr"\delta = 9.87(1 - \alpha + \beta \bar{{\lambda}}) + \bar{{\lambda}}^2 = 9.87(1 - {alpha} + {res_compression['beta']} \cdot {lambda_bar:.3f}) + {lambda_bar:.3f}^2 = {delta:.3f}")
                    st.latex(fr"\varphi = \frac{{0.5 (\delta - \sqrt{{\delta^2 - 39.48 \bar{{\lambda}}^2}})}}{{\bar{{\lambda}}^2}} = \frac{{0.5 ({delta:.3f} - \sqrt{{{delta:.3f}^2 - 39.48 \cdot {lambda_bar:.3f}^2}})}}{{{lambda_bar:.3f}^2}} = \mathbf{{{phi_val:.3f}}}")
                
                st.markdown(fr"Определение температурного коэффициента снижения прочности стальных элементов при {load_type.lower()}")
                tex_gamma_eq = r"\gamma_T = \frac{N}{\varphi \cdot A \cdot R_{yn} \cdot \gamma_c}"
                tex_gamma_sub = fr"\frac{{{n_newton:.0f}}}{{{phi_val:.3f} \cdot {fmt_latex_sci(props_si['A'])} \cdot {fmt_latex_ryn_mpa(ryn_pascal)} \cdot {gamma_c}}}"
                st.latex(fr"{tex_gamma_eq} = {tex_gamma_sub} = \mathbf{{{gamma_t:.4f}}}")

            elif load_type == "Изгиб":
                st.write("Расчет на изгиб (Moment) и сдвиг (Shear). Берется худший случай.")
                # Bending Display
                st.markdown(r"**Изгиб:**")
                
                # Display c1 calculation details
                st.markdown(r"*Определение коэффициента $c_1$ (учет пластических деформаций):*")
                # Retrieve af/aw from props_mm which we ensured are there for I/Channel
                af_disp = props_mm.get("Af", 0)
                aw_disp = props_mm.get("Aw", 0)
                
                if af_disp > 0 and aw_disp > 0:
                     # Calculate component formulas
                     h_val = geom_params.get('h_mm', 0)
                     b_val = geom_params.get('b_mm', 0)
                     tw_val = geom_params.get('tw_mm', 0)
                     tf_val = geom_params.get('tf_mm', 0)
                     
                     st.write(r"Расчет площадей полки ($A_f$) и стенки ($A_w$):")
                     
                     # Formula depends on section type but generally Af=b*tf, Aw=(h-2tf)*tw for I/Channel
                     if section_code in ["ibeam", "channel"]:
                        st.latex(fr"A_f = b \cdot t_f = {b_val:.0f} \cdot {tf_val:.1f} = \mathbf{{{af_disp:.1f}}} \text{{ мм}}^2")
                        st.latex(fr"A_w = (h - 2t_f) \cdot t_w = ({h_val:.0f} - 2\cdot{tf_val:.1f}) \cdot {tw_val:.1f} = \mathbf{{{aw_disp:.1f}}} \text{{ мм}}^2")
                     
                     n_ratio = af_disp / aw_disp
                     st.latex(fr"n = \frac{{A_f}}{{A_w}} = \frac{{{af_disp:.1f}}}{{{aw_disp:.1f}}} = \mathbf{{{n_ratio:.2f}}}")
                     
                     # Interpolation Display
                     if c1_res and c1_res.get("trace"):
                        tr = c1_res["trace"]
                        st.markdown(fr"По Таблице Е.1 (СП 16.13330): Интерполяция для $n={n_ratio:.2f}$")
                        st.write(fr"При $n={tr['low'][0]}$ $\to$ $c_1={tr['low'][1]}$")
                        st.write(fr"При $n={tr['high'][0]}$ $\to$ $c_1={tr['high'][1]}$")
                        
                        st.latex(fr"c_1 = {tr['eq']} = {c1_val:.3f}")
                        st.write(fr"Итого: $\mathbf{{c_1 = {c1_val:.3f}}}$")
                     else:
                        st.markdown(fr"По Таблице Е.1 (СП 16.13330): $\Rightarrow c_1 = \mathbf{{{c1_val:.3f}}}$")
                else:
                     st.write(f"Принимается $c_1 = {c1_val:.3f}$ (для данного типа сечения)")

                tex_bend_eq = r"\gamma_T = \frac{M}{c_1 \cdot W_x \cdot R_{yn}}"
                tex_bend_sub = fr"\frac{{{m_newton_m:.0f}}}{{{c1_val:.3f} \cdot {fmt_latex_sci(props_si.get('Wx',0))} \cdot {fmt_latex_ryn_mpa(ryn_pascal)}}}"
                st.latex(fr"{tex_bend_eq} = {tex_bend_sub} = \mathbf{{{gamma_t_bending:.4f}}}")
                
                # Shear Display
                st.markdown(r"**Сдвиг:**")
                tex_shear_eq = r"\gamma_T = \frac{Q \cdot S_x}{I_x \cdot t_w \cdot R_s}"
                tex_shear_sub = fr"\frac{{{q_newton:.0f} \cdot {fmt_latex_sci(props_si.get('Sx',0))}}}{{{fmt_latex_sci(props_si.get('Ix',1))} \cdot {fmt_latex_sci(props_si.get('tw',1))} \cdot 0.58 \cdot {fmt_latex_ryn_mpa(ryn_pascal)}}}"
                st.latex(fr"{tex_shear_eq} = {tex_shear_sub} = \mathbf{{{gamma_t_shear:.4f}}}")
        
            # Critical Temp Calculation Display (Moved here, dedented)
            st.divider()
            st.markdown(r"**Определение критической температуры**")
            trace = crit_result.get("trace")
            if trace:
                st.write(f"Интерполяция по Таблице Б.1 для стали {steel_grade}")
                tex_crit_eq = r"t_{cr} = T_1 + \frac{\gamma_T - \gamma_1}{\gamma_2 - \gamma_1} (T_2 - T_1)"
                tex_crit_sub = fr"{trace['t1']} + \frac{{{gamma_t:.4f} - {trace['g1']:.2f}}}{{{trace['g2']:.2f} - {trace['g1']:.2f}}} ({trace['t2']} - {trace['t1']})"
                st.latex(fr"{tex_crit_eq} = {tex_crit_sub} = \mathbf{{{crit_temp:.1f}}} ^\circ C")
            else:
                # Boundary cases
                if gamma_t >= 1.0:
                    st.write(r"Так как температурный коэффициент снижения прочности стального элемента $\gamma_T \ge 1.0$, критическая температура принимается равной начальной температуре:")
                    st.latex(fr"\gamma_T = {gamma_t:.4f} \ge 1.0 \Rightarrow t_{{cr}} = 20 ^\circ C")
                elif crit_temp >= 800: # Assuming 800 is max in data.py
                    st.write(r"Так как температурный коэффициент снижения прочности стального элемента крайне мал, критическая температура превышает 800 °C:")
                    st.latex(fr"\gamma_T = {gamma_t:.4f} \Rightarrow t_{{cr}} = 800 ^\circ C (\text{{макс. по таблице}})")
                else: 
                     st.write("Значение совпадает с табличным (интерполяция не требуется):")
                     st.latex(fr"\gamma_T = {gamma_t:.4f} \Rightarrow t_{{cr}} = {crit_temp:.1f} ^\circ C")

        # 2. Thermal Calc Details
        with st.expander("2. Теплотехническая задача", expanded=True):
            # Define formula string based on section and exposure
            p_formula_tex = ""
            p_subst_tex = ""
            
            
            if section_code == "ibeam":
                h, b, tw = geom_params['h_mm'], geom_params['b_mm'], geom_params['tw_mm']
                if exposure_mode == "4_sides":
                    p_formula_tex = r"2h + 4b - 2t_w"
                    p_subst_tex = fr"2 \cdot {h:.0f} + 4 \cdot {b:.0f} - 2 \cdot {tw:.1f}"
                else: 
                    p_formula_tex = r"2h + 3b - 2t_w"
                    p_subst_tex = fr"2 \cdot {h:.0f} + 3 \cdot {b:.0f} - 2 \cdot {tw:.1f}"
            
            elif section_code == "channel":
                h, b, tw = geom_params['h_mm'], geom_params['b_mm'], geom_params['tw_mm']
                if exposure_mode == "4_sides":
                    p_formula_tex = r"2h + 4b - 2t_w"
                    p_subst_tex = fr"2 \cdot {h:.0f} + 4 \cdot {b:.0f} - 2 \cdot {tw:.1f}"
                else: 
                    p_formula_tex = r"2h + 3b - 2t_w" 
                    p_subst_tex = fr"2 \cdot {h:.0f} + 3 \cdot {b:.0f} - 2 \cdot {tw:.1f}"

            elif section_code == "angle":
                b = geom_params.get('b_mm', 0)
                # User formula P = 2b1 + 2b2 = 4b
                p_formula_tex = r"2b + 2b = 4b"
                p_subst_tex = fr"4 \cdot {b:.0f}"
                    
            elif section_code == "rect_tube":
                h, b = geom_params['h_mm'], geom_params['b_mm']
                if exposure_mode == "4_sides":
                    p_formula_tex = r"2(h + b)"
                    p_subst_tex = fr"2({h:.0f} + {b:.0f})"
                else:
                    p_formula_tex = r"2h + b"
                    p_subst_tex = fr"2 \cdot {h:.0f} + {b:.0f}"
                    
            elif section_code == "circ_tube":
                d = geom_params['d_mm']
                p_formula_tex = r"\pi \cdot d"
                p_subst_tex = fr"\pi \cdot {d:.0f}"

            # Removed Schema and Area text

            st.markdown("Определение приведенной толщины металла:")
            
            # Detailed Reduced Thickness Formula with Perimeter expansion
            st.latex(fr"\delta_{{np}} = \frac{{A}}{{\Pi}} = \frac{{A}}{{{p_formula_tex}}} = \frac{{{props_si['A']*1e6:.0f}}}{{{p_subst_tex}}} = \frac{{{props_si['A']*1e6:.0f}}}{{{perimeter_mm:.0f}}} = \mathbf{{{delta_np_mm:.2f}}} \text{{ мм}}")
            
            st.divider()
            
            # Graph moved from Overview
            if fire_res_result:
                df = fire_res_result['history']
                fig = go.Figure()
                # Standard Fire: Red, Solid (width 2 default or explicit)
                fig.add_trace(go.Scatter(x=df['Time_min'], y=df['T_gas'], name='Стандартный температурный режим пожара', line=dict(color='red', width=2)))
                # Steel curve: Black Dashed
                fig.add_trace(go.Scatter(x=df['Time_min'], y=df['T_steel'], name='Температура конструкции', line=dict(color='black', width=2, dash='dash')))
                
                fig.update_layout(
                    title=dict(text="График нагрева стальной конструкции", x=0.5, xanchor='center', yanchor='top'), # Centered Title
                    xaxis_title="Время (мин)",
                    yaxis_title="Температура (°C)",
                    height=500,
                    xaxis=dict(range=[0, 60], dtick=5, showgrid=False, zeroline=False, linecolor='black', linewidth=2, ticks='outside', tickwidth=2, tickcolor='black', tickfont=dict(color='black'), title_font=dict(size=14, color='black')),
                    yaxis=dict(dtick=100, rangemode="tozero", showgrid=False, zeroline=False, linecolor='black', linewidth=2, ticks='outside', tickwidth=2, tickcolor='black', tickfont=dict(color='black'), title_font=dict(size=14, color='black')),
                    plot_bgcolor='white', # Clean white background
                    margin=dict(l=20, r=20, t=40, b=20),
                    hovermode="x unified",
                    legend=dict(
                        x=0.99, y=0.01,
                        xanchor="right", yanchor="bottom",
                        bgcolor="rgba(255, 255, 255, 0.8)", # Transparent white
                        bordercolor="white", borderwidth=0 # No border for legend as per clean look, or keep it? User said "like screenshot". Screenshot has NO legend visible or maybe hidden? I'll make it clean but keep it for clarity with simple style.
                        # Wait, user screenshot example has NO legend box. Just curves.
                        # But I should probably keep legend for user to know which is which. 
                        # I'll keep default simple legend but maybe no border.
                    )
                )

                # Visual markers for Critical Point
                fire_res_val = fire_res_result["raw_time"]
                
                if isinstance(fire_res_val, (int, float)) and fire_res_val < 60.0:
                     # Dashed Vertical Line
                    fig.add_shape(
                        type="line",
                        x0=fire_res_val, y0=0,
                        x1=fire_res_val, y1=crit_temp,
                        line=dict(color="black", width=1, dash="dot"),
                    )
                    
                     # Dashed Horizontal Line
                    fig.add_shape(
                        type="line",
                        x0=0, y0=crit_temp,
                        x1=fire_res_val, y1=crit_temp,
                        line=dict(color="black", width=1, dash="dot"),
                    )
                    
                    # Add Red Dot
                    fig.add_trace(go.Scatter(
                        x=[fire_res_val],
                        y=[crit_temp],
                        mode='markers',
                        marker=dict(color='red', size=12, line=dict(color='white', width=1)),
                        showlegend=False,
                        name='Critical Point'
                    ))
                    
                    # Add Text Label near X-axis
                    fig.add_annotation(
                        x=fire_res_val,
                        y=0,
                        text=f"{fire_res_val:.1f} мин",
                        showarrow=False,
                        yshift=10,
                        xshift=35, # Shift to right slightly
                        font=dict(color="red", size=12)
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Кнопки экспорта данных
                col_exp1, col_exp2 = st.columns(2)
                with col_exp1:
                    # Экспорт данных в CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📊 Скачать данные (CSV)",
                        data=csv,
                        file_name=f"fire_resistance_data_{section_type_ui}_{steel_grade}.csv",
                        mime="text/csv",
                        help="Скачать историю нагрева в формате CSV"
                    )

                with col_exp2:
                    # Экспорт графика в HTML (интерактивный)
                    html_str = fig.to_html()
                    st.download_button(
                        label="📈 Скачать график (HTML)",
                        data=html_str,
                        file_name=f"fire_resistance_chart_{section_type_ui}.html",
                        mime="text/html",
                        help="Скачать интерактивный график в формате HTML"
                    )

                st.divider()

                # Fire Resistance Text Output
                r_result_val = fire_res_result['raw_time']
                st.write(f"⏱️ Время прогрева стальной конструкции до критической температуры равно **{r_result_val:.1f} мин**.")

                r_int = int(r_result_val)
                st.markdown(r"🔥 Предел огнестойкости стальной конструкции равен $\Pi_\phi = R" + str(r_int) + r"$")
            
            # Also show Am/V as it's used internally
            # (Calculation hidden as per user request, using reduced thickness instead)
            
    # --- TAB 4: REPORT ---
    with tab_report:
        st.header("Генерация отчета")
        st.info("Введите данные об объекте для формирования отчета в формате .docx")
        
        with st.form("report_form"):
            col_rep1, col_rep2 = st.columns(2)
            with col_rep1:
                obj_name = st.text_input("Наименование объекта защиты", value="Торговый центр 'Пример'")
                obj_address = st.text_input("Адрес объекта", value="г. Москва, ул. Строителей, д. 1")
            with col_rep2:
                req_fire_res = st.selectbox("Требуемый предел огнестойкости", [15, 30, 45, 60, 90, 120, 150, 180, 240], index=1)
                obj_desc = st.text_area("Краткая характеристика объекта", value=f"Стальная колонна ({section_type_ui}). Сталь {steel_grade}.", height=100)
            
            submitted = st.form_submit_button("Подготовить данные")
            
        if submitted:
            # Collect data
            report_data = {
                "object_name": obj_name,
                "object_address": obj_address,
                "object_desc": obj_desc,
                "required_fire_res": req_fire_res,
                "calc_params": {
                    "load_type": load_type,
                    "n_load": n_newton if load_type != "Изгиб" else q_newton, # Approx
                    "section_type": section_type_ui,
                    "profile_name": section_type_ui,
                    "steel_grade": steel_grade,
                },
                "results": {
                    "gamma_t": gamma_t if load_type != "Изгиб" else max(gamma_t_bending, gamma_t_shear),
                    "crit_temp": crit_temp,
                    "delta_np": delta_np_mm,
                    "limit_time": fire_res_result["raw_time"],
                    "limit_time_str": f"R {fire_res_result['raw_time']:.0f}",
                    "geom_props": props_si
                }
            }
            
            # Generate Graph Image (опционально)
            if 'fig' in locals() and fig:
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
                    report_data['results']['graph_image'] = img_bytes
                    st.toast("✅ График успешно добавлен в отчет", icon="📊")
                except Exception as e:
                    # Kaleido не установлен - отчет будет без графика
                    st.toast("⚠️ График не добавлен: установите kaleido", icon="⚠️")
                    st.info("💡 Совет: Выполните `pip install kaleido` для добавления графиков в отчет")
            
            # Generate doc
            try:
                from src.report_generator import create_report
                from io import BytesIO
                
                doc = create_report(report_data)
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                # Store in session state to persist after reload
                st.session_state['report_buffer'] = buffer
                st.session_state['report_generated'] = True
                st.toast("✅ Отчет успешно создан!", icon="📄")

            except Exception as e:
                st.error(f"❌ Ошибка при генерации отчета: {e}")
                st.toast("⚠️ Ошибка генерации отчета", icon="⚠️")
                st.warning("💡 Убедитесь, что установлен пакет python-docx: `pip install python-docx`")

        if st.session_state.get('report_generated'):
             st.success("✅ Отчет успешно сформирован!")
             buf = st.session_state['report_buffer']
             buf.seek(0)
             st.download_button(
                    label="📥 Скачать отчет (.docx)",
                    data=buf.getvalue(),
                    file_name="fire_resistance_report.docx",
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )

    # --- TAB 3: VALIDATION ---
    with tab_validation:
        st.header("🔬 Валидация модели прогрева")
        st.markdown("""
        График прогрева стальной конструкции при стандартном температурном режиме пожара
        для различных значений приведенной толщины металла.
        """)

        # Фиксированные параметры расчета
        max_time_validation = 60  # мин
        crit_temp_validation = 500  # °C

        # Приведенные толщины для расчета
        thicknesses = [3, 5, 10, 15, 20]  # мм

        # Выполняем расчеты для разных толщин
        with st.spinner("Выполняется расчет прогрева..."):
            # Создаем график
            fig_validation = go.Figure()

            # Цветовая палитра
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

            # Добавляем стандартную температурную кривую (первой в легенде)
            time_points = np.linspace(0, max_time_validation, 200)
            temp_gas = [thermal.standard_fire_curve(t * 60) - 273.15 for t in time_points]

            fig_validation.add_trace(go.Scatter(
                x=time_points,
                y=temp_gas,
                mode='lines',
                name='Стандартный температурный режим',
                line=dict(color='red', width=2, dash='dash'),
                hovertemplate='<b>Стандартный температурный режим</b><br>' +
                              'Время: %{x:.1f} мин<br>' +
                              'Температура: %{y:.0f} °C<br>' +
                              '<extra></extra>'
            ))

            # Добавляем кривые прогрева для разных толщин
            for i, delta_np in enumerate(thicknesses):
                # Рассчитываем Am_V (коэффициент сечения)
                # Am_V = P/A = 1/delta_np (в м)
                am_v = 1000.0 / delta_np  # Переводим мм в м: 1/м

                # Выполняем расчет прогрева
                fire_res = thermal.calculate_fire_resistance(
                    Am_V=am_v,
                    crit_temp=crit_temp_validation,
                    protection_type="unprotected",
                    max_time_min=max_time_validation
                )

                # Добавляем линию на график
                history = fire_res["history"]
                fig_validation.add_trace(go.Scatter(
                    x=history["Time_min"],
                    y=history["T_steel"],
                    mode='lines',
                    name=f'δnp = {delta_np} мм',
                    line=dict(color=colors[i], width=2.5),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'Время: %{x:.1f} мин<br>' +
                                  'Температура: %{y:.0f} °C<br>' +
                                  '<extra></extra>'
                ))

            # Настройка графика
            fig_validation.update_layout(
                title=dict(
                    text="Прогрев стальной конструкции при стандартном пожаре",
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(size=18, family="Arial")
                ),
                xaxis=dict(
                    title="Время, мин",
                    range=[0, max_time_validation],
                    showgrid=False,
                    zeroline=False,
                    linecolor='black',
                    linewidth=2,
                    ticks='outside',
                    tickwidth=2,
                    tickcolor='black',
                    tickfont=dict(color='black'),
                    title_font=dict(size=14, color='black')
                ),
                yaxis=dict(
                    title="Температура, °C",
                    rangemode="tozero",
                    showgrid=False,
                    zeroline=False,
                    linecolor='black',
                    linewidth=2,
                    ticks='outside',
                    tickwidth=2,
                    tickcolor='black',
                    tickfont=dict(color='black'),
                    title_font=dict(size=14, color='black')
                ),
                legend=dict(
                    title="Легенда",
                    orientation="v",
                    yanchor="bottom",
                    y=0.01,
                    xanchor="right",
                    x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="gray",
                    borderwidth=1
                ),
                hovermode='x unified',
                plot_bgcolor='white',
                height=600,
                margin=dict(l=60, r=40, t=80, b=60)
            )

            # Добавление экспериментальных данных из файла Книга1.xlsx
            try:
                import os
                exp_file_path = os.path.join(os.path.dirname(__file__), "Книга1.xlsx")

                if os.path.exists(exp_file_path):
                    exp_data = pd.read_excel(exp_file_path)

                    # Маркеры для экспериментальных данных
                    exp_markers = ['circle', 'square', 'diamond', 'cross', 'x']

                    # Добавляем экспериментальные данные для каждой толщины
                    exp_columns = {
                        "3 мм": (3, colors[0]),
                        "5 мм": (5, colors[1]),
                        "10 мм": (10, colors[2]),
                        "15 мм": (15, colors[3]),
                        "20 мм": (20, colors[4])
                    }

                    for idx, (col_name, (delta_np, color)) in enumerate(exp_columns.items()):
                        if col_name in exp_data.columns:
                            # Фильтруем NaN значения
                            valid_data = exp_data[['Время, мин', col_name]].dropna()

                            if not valid_data.empty:
                                fig_validation.add_trace(go.Scatter(
                                    x=valid_data['Время, мин'],
                                    y=valid_data[col_name],
                                    mode='markers',
                                    name=f'Эксперимент δnp = {delta_np} мм',
                                    marker=dict(
                                        size=10,
                                        color=color,
                                        symbol=exp_markers[idx],
                                        line=dict(width=2, color='white')
                                    ),
                                    hovertemplate='<b>Эксперимент δnp = ' + str(delta_np) + ' мм</b><br>' +
                                                  'Время: %{x:.1f} мин<br>' +
                                                  'Температура: %{y:.0f} °C<br>' +
                                                  '<extra></extra>'
                                ))
            except Exception as e:
                # Если файл не найден или ошибка чтения - продолжаем без экспериментальных данных
                pass

            # Отображение графика
            st.plotly_chart(fig_validation, use_container_width=True)


if __name__ == "__main__":
    main()
