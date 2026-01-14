import math

# -------------------------------------------------------------------
# BENDING & FLANGE HELPERS
# -------------------------------------------------------------------

def calc_c1_coefficient(af, aw):
    """
    Расчет коэффициента c1 (учет развития пластических деформаций).
    Для двутавра: n = Af / Aw.
    Интерполяция по Таблице Е.1 СП 16.13330 (или Б.9 пособия).
    Упрощенная аппроксимация по данным из примера (n=0.5 -> c=1.07, n=1.0 -> c=1.12).
    """
    if aw <= 0: 
        return {
            "value": 1.0,
            "n": 0,
            "trace": None
        }
    n = af / aw
    
    # Линейная интерполяция между (0.5, 1.07) и (1.0, 1.12) как в примере
    # c1 = 1.07 + (n - 0.5) * (1.12 - 1.07) / (1.0 - 0.5)
    # c1 = 1.07 + (n - 0.5) * 0.1
    c1 = 1.07 + (n - 0.5) * 0.1
    
    # Ограничим разумными пределами, т.к. таблица шире
    if c1 < 1.0: c1 = 1.0
    if c1 > 1.2: c1 = 1.2 # Примерный верхний предел для двутавров
    
    return {
        "value": c1,
        "n": n,
        "trace": {
            "low": (0.5, 1.07),
            "high": (1.0, 1.12),
            "eq": r"1.07 + (n - 0.5) \cdot \frac{1.12 - 1.07}{1.0 - 0.5}"
        }
    }

def calc_gamma_bending(m_load, w_section, ry, gamma_c=1.0, c1=1.0):
    """
    Расчет gamma_T для изгиба (Формула 4.6).
    val = M / (c1 * W * Ry * gamma_c)
    """
    if w_section <= 0: return 999
    # W_pl_min = Wx * c1
    w_pl = w_section * c1
    val = m_load / (w_pl * ry * gamma_c)
    return val

def calc_gamma_shear(q_load, sx, ix, tw, ry, gamma_c=1.0):
    """
    Расчет gamma_T для сдвига/поперечной силы (Формула из примера 1 п. 5.2).
    gamma_T = (Q * Sx) / (Ix * tw * Rs * gamma_c)
    Rs = 0.58 * Ry (сдвиговая прочность)
    """
    if ix <= 0 or tw <= 0: return 999
    
    rs = 0.58 * ry
    val = (q_load * sx) / (ix * tw * rs * gamma_c)
    return val


# -------------------------------------------------------------------
# GEOMETRY HELPERS UPDATE
# -------------------------------------------------------------------

def calculate_geometry_ibeam(h_mm, b_mm, tw_mm, tf_mm):
    """
    Расчет геометрии двутавра.
    """
    # Areas
    af = b_mm * tf_mm # Area of one flange
    h_web = h_mm - 2 * tf_mm
    aw = h_web * tw_mm # Area of web
    area = 2 * af + aw
    
    # Inertia Ix (Strong axis)
    # I = (b*h^3)/12 - 2*((b-tw)/2 * (h-2tf)^3)/12
    b_inner = (b_mm - tw_mm) / 2.0
    
    ix_val = (b_mm * h_mm**3) / 12.0 - 2 * (b_inner * h_web**3) / 12.0
    
    # Inertia Iy (Weak axis)
    iy_flanges = 2 * (tf_mm * b_mm**3) / 12.0
    iy_web = (h_web * tw_mm**3) / 12.0
    iy_val = iy_flanges + iy_web
    
    # Radii of Gyration
    i_x = math.sqrt(ix_val / area) if area > 0 else 0
    i_y = math.sqrt(iy_val / area) if area > 0 else 0
    
    # Section Modulus Wx
    wx = ix_val / (h_mm / 2.0)
    
    # Static Moment Sx (Half-section moment of area about neutral axis)
    # Sx = Af * dist_f + Aw_half * dist_w
    # dist_f (center of flange) = h/2 - tf/2
    # dist_w (center of half web) = (h/2 - tf)/2 + ... simplify:
    # Sx = b*tf*(h/2 - tf/2) + tw*(h/2 - tf)*( (h/2 - tf)/2 )
    
    dist_f = h_mm/2.0 - tf_mm/2.0
    h_half_web = h_web / 2.0
    dist_w = h_half_web / 2.0
    
    sx = af * dist_f + (tw_mm * h_half_web) * dist_w
    
    return {
        "A": area,
        "Ix": ix_val,
        "Iy": iy_val,
        "ix": i_x,
        "iy": i_y,
        "Wx": wx,
        "Sx": sx,
        "Af": af,
        "Aw": aw,
        "tw": tw_mm,
        "type": "ibeam"
    }

def calculate_geometry_rect_tube(h_mm, b_mm, t_mm):
    """
    Прямоугольная труба.
    """
    # Outer
    area_outer = h_mm * b_mm
    ix_outer = (b_mm * h_mm**3) / 12.0
    iy_outer = (h_mm * b_mm**3) / 12.0
    
    # Inner
    h_in = h_mm - 2*t_mm
    b_in = b_mm - 2*t_mm
    
    if h_in < 0 or b_in < 0: return {"A":0, "Ix":0, "Iy":0, "ix":0, "iy":0, "Wx":0, "Sx":0, "type": "rect_tube"}
    
    area_inner = h_in * b_in
    ix_inner = (b_in * h_in**3) / 12.0
    iy_inner = (h_in * b_in**3) / 12.0
    
    area = area_outer - area_inner
    ix_val = ix_outer - ix_inner
    iy_val = iy_outer - iy_inner
    
    i_x = math.sqrt(ix_val / area) if area > 0 else 0
    i_y = math.sqrt(iy_val / area) if area > 0 else 0
    
    wx = ix_val / (h_mm / 2.0)
    
    # Sx approx (hollow rect)
    # Sx_outer - Sx_inner
    sx_outer = (b_mm * h_mm**2) / 8.0
    sx_inner = (b_in * h_in**2) / 8.0
    sx = sx_outer - sx_inner

    # Flange/Web conceptual separation for tube is tricky, usually not used for c1 in simple theory
    # But for shear we need tw (sum of 2 webs)
    tw_eff = 2 * t_mm 

    return {
        "A": area,
        "Ix": ix_val,
        "Iy": iy_val,
        "ix": i_x,
        "iy": i_y,
        "Wx": wx,
        "Sx": sx,
        "tw": tw_eff,
        "type": "rect_tube"
    }

def calculate_geometry_circ_tube(d_mm, t_mm):
    """
    Круглая труба.
    """
    d_in = d_mm - 2 * t_mm
    if d_in < 0: return {"A":0, "Ix":0, "Iy":0, "ix":0, "iy":0, "Wx":0, "Sx":0, "type": "circ_tube"}
    
    area = math.pi * (d_mm**2 - d_in**2) / 4.0
    
    # I = pi * (D^4 - d^4) / 64
    ix_val = math.pi * (d_mm**4 - d_in**4) / 64.0
    iy_val = ix_val
    
    i_x = math.sqrt(ix_val / area) if area > 0 else 0
    i_y = i_x
    
    wx = ix_val / (d_mm / 2.0)
    
    # Sx for circle = D^3/12 - d^3/12 ? No, for Circle Sx = D^3/12 is false.
    # Sx = 2/3 * (R_out^3 - R_in^3) ?
    # Exact: 2/3 * (r_o^3 - r_i^3)
    r_o = d_mm / 2.0
    r_i = d_in / 2.0
    sx = (2.0/3.0) * (r_o**3 - r_i**3)
    
    # tw effective? for shear in pipe usually special formula, but let's approx if needed
    # For tubes shear logic usually diff. We will enable Shear only for I-Beam or generic.

    return {
        "A": area,
        "Ix": ix_val,
        "Iy": iy_val,
        "ix": i_x,
        "iy": i_y,
        "Wx": wx,
        "Sx": sx,
        "type": "circ_tube"
    }

def get_phi_coeffs(section_type, is_box_channel=False):
    """
    Возвращает коэффициенты alpha, beta и дополнительные параметры для расчета fi.
    По Таблице 4.1 (СП 16.13330 / Пособие).

    Args:
        section_type: тип сечения
        is_box_channel: True если это коробчатое сечение из двух швеллеров

    Returns:
        alpha (float)
        beta (float)
        threshold (float): Порог гибкости для формулы 7.6/lambda^2 (3.8 для a, 4.4 для b, 5.8 для c)
        curve_code (str): 'a', 'b' или 'c'
    """
    if section_type == "circ_tube" or section_type == "rect_tube":
        # Curve 'a' (0.03, 0.06) - Tubes (Pipe, Rect Tube)
        # Threshold 3.8
        return 0.03, 0.06, 3.8, 'a'
    elif section_type == "channel":
        # Для коробчатого сечения из двух швеллеров используем кривую 'b'
        if is_box_channel:
            # Curve 'b' (0.04, 0.09) - Box section from two channels
            # Threshold 4.4
            return 0.04, 0.09, 4.4, 'b'
        else:
            # Curve 'c' (0.04, 0.14) - Single Channels (Швеллер)
            # Threshold 5.8
            return 0.04, 0.14, 5.8, 'c'
    elif section_type == "ibeam":
        # Curve 'b' (0.04, 0.09) - Rolled I-beams
        # Threshold 4.4
        return 0.04, 0.09, 4.4, 'b'
    elif section_type == "angle":
        # Curve 'b' for angles (rolled)
        return 0.04, 0.09, 4.4, 'b'
    else:
        # Default curve b
        return 0.04, 0.09, 4.4, 'b'

def calc_phi(lambda_val, ry, e_modulus, alpha, beta, threshold=999, curve_code='b'):
    """
    Рассчитывает коэффициент устойчивости fi.
    
    Args:
        lambda_val: Максимальная гибкость (lambda_max)
        ry: Ry (Pa)
        e_modulus: E (Pa)
        alpha, beta: коэффициенты кривой
        threshold: порог гибкости для переключения формулы
        curve_code: код кривой ('a', 'b', 'c')
    
    Returns (phi, delta, lambda_bar, method_info)
        method_info: строка, описывающая примененный метод ('standard', 'low_lambda', 'high_lambda')
    """
    # Расчет условной гибкости lambda_bar
    if ry <= 0 or e_modulus <= 0: return 0,0,0, 'error'
    
    lambda_bar = lambda_val * math.sqrt(ry / e_modulus)
    
    method = 'standard'
    
    # 1. Low Lambda Cap (only for curves a, b)
    if lambda_bar < 0.6 and curve_code in ['a', 'b']:
        return 1.0, 0.0, lambda_bar, 'low_lambda'

    # 2. High Lambda Formula (Euler-like)
    if lambda_bar > threshold:
        # phi = 7.6 / lambda_bar^2
        if lambda_bar > 0:
            phi = 7.6 / (lambda_bar**2)
            return phi, 0.0, lambda_bar, 'high_lambda'
        else:
            return 0.0, 0.0, lambda_bar, 'error'
            
    # 3. Standard Formula
    # delta = 9.87 * (1 - alpha + beta * lambda_bar) + lambda_bar^2
    delta = 9.87 * (1 - alpha + beta * lambda_bar) + lambda_bar**2
    
    discriminant = delta**2 - 39.48 * (lambda_bar**2)
    
    if discriminant < 0:
        # Should not happen for valid ranges, but safety
        return 0.1, delta, lambda_bar, 'error'

    if lambda_bar <= 0: return 1.0, 0.0, lambda_bar, 'low_lambda' # Safety for 0
    
    phi = (0.5 * (delta - math.sqrt(discriminant))) / (lambda_bar**2)
    
    return phi, delta, lambda_bar, 'standard'

def calc_gamma_tension(n_load, area, ry, gamma_c=1.0):
    """
    Расчет коэффициента при центральном растяжении.
    """
    if area <= 0 or ry <= 0: return 0
    val = n_load / (area * ry * gamma_c)
    return val

def calc_gamma_compression_stability(n_load, area, ry, e_modulus, lef_x, lef_y, ix, iy, section_type, gamma_c=1.0, is_box_channel=False):
    """
    Расчет коэффициента при центральном сжатии с учетом устойчивости.
    Возвращает словарь с результатом и промежуточными значениями.

    Args:
        is_box_channel: True если это коробчатое сечение из двух швеллеров
    """
    if area <= 0 or ry <= 0:
        return {"val": 0, "phi": 0, "lambda_bar": 0, "lambda_val": 0, "axis": "N/A", "delta": 0, "alpha": 0, "beta": 0, "method": "error", "threshold": 0, "curve_code": "?"}

    # Гибкости
    lambda_x = lef_x / ix if ix > 0 else 999
    lambda_y = lef_y / iy if iy > 0 else 999

    # Максимальная гибкость определяет расчет
    lambda_max = max(lambda_x, lambda_y)
    axis = "x" if lambda_x >= lambda_y else "y"

    # Коэффициенты alpha, beta, threshold, curve_code
    alpha, beta, threshold, curve_code = get_phi_coeffs(section_type, is_box_channel)
    
    # Расчет фи и условной гибкости
    phi, delta, lambda_bar, method = calc_phi(lambda_max, ry, e_modulus, alpha, beta, threshold, curve_code)
    
    if phi <= 0: 
        val = 999
    else:
        val = n_load / (phi * area * ry * gamma_c)
        
    return {
        "val": val,
        "phi": phi,
        "lambda_bar": lambda_bar,
        "lambda_val": lambda_max,
        "axis": axis,
        "lambda_x": lambda_x,
        "lambda_y": lambda_y,
        "delta": delta,
        "alpha": alpha, 
        "beta": beta,
        "threshold": threshold,
        "curve_code": curve_code,
        "method": method
    }

def calculate_geometry_channel(h_mm, b_mm, tw_mm, tf_mm):
    """
    Расчет геометрии швеллера (упрощенно как швеллер с параллельными гранями полок).
    """
    # 1. Площадь A
    # Геометрически:
    # 2 полки размером b * tf
    area_flanges = 2 * (b_mm * tf_mm)
    # Стенка между полками: (h - 2*tf) * tw
    area_web = (h_mm - 2 * tf_mm) * tw_mm
    
    area = area_flanges + area_web
    
    # 2. Момент инерции Ix (относительно главной оси X - горизонтальной)
    # I_x = (b * h^3)/12 - ((b - tw) * (h - 2*tf)^3)/12
    # Разница внешнего прямоугольника (b x h) и внутреннего ((b-tw) x (h-2tf))
    ix_mm4 = (b_mm * h_mm**3)/ 12.0 - ((b_mm - tw_mm) * (h_mm - 2 * tf_mm)**3) / 12.0
    
    # 3. Момент инерции Iy (нужен центр тяжести x_c от внешней грани стенки)
    # Ось Y проходит перпендикулярно полкам.
    # Центр тяжести относительно внешней грани стенки (x=0)
    
    # Полки:
    # Центр тяжести каждой полки: x_f = b_mm / 2.0
    # Площадь: b * tf
    
    # Стенка:
    # Центр тяжести стенки: x_w = tw_mm / 2.0
    # Площадь: (h - 2*tf) * tw
    
    x_c = (area_flanges * (b_mm / 2.0) + area_web * (tw_mm / 2.0)) / area
    
    # Iy = Sum(Ii + Ai * di^2)
    # Для полок (их 2 штук):
    # I_yf = (tf * b^3) / 12
    # dist_f = (b/2) - x_c
    iy_flanges = 2 * ((tf_mm * b_mm**3) / 12.0 + (b_mm * tf_mm) * (b_mm/2.0 - x_c)**2)
    
    # Для стенки:
    # I_yw = ((h-2tf) * tw^3) / 12
    # dist_w = (tw/2) - x_c
    iy_web = ((h_mm - 2 * tf_mm) * tw_mm**3) / 12.0 + area_web * (tw_mm/2.0 - x_c)**2
    
    iy_mm4 = iy_flanges + iy_web
    
    # Радиусы инерции
    import math
    try:
        ix_rad = math.sqrt(ix_mm4 / area)
        iy_rad = math.sqrt(iy_mm4 / area)
    except:
        ix_rad = 0
        iy_rad = 0
        
    res = {
        "A": area,
        "Ix": ix_mm4,
        "Iy": iy_mm4,
        "ix": ix_rad,
        "iy": iy_rad
    }
    
    # Wx = Ix / (h/2)
    res["Wx"] = ix_mm4 / (h_mm / 2.0)
    
    # Store components for C1 calculation
    res["Af"] = area_flanges / 2.0 # Wait, area_flanges was 2*b*tf. Per flange is /2.
    res["Aw"] = area_web
    res["tw"] = tw_mm
    res["type"] = "channel"
    
    return res
