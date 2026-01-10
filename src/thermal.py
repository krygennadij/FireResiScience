import math

def standard_fire_curve(t_sec):
    """
    Стандартная кривая пожара.
    Tg_tau = 345 * log10((8/60)*tau + 1) + T0
    
    Args:
        t_sec: Время в секундах (tau).
        
    Returns:
        Температура газовой среды в Кельвинах (T0 = 293 K).
    """
    T0 = 293.0
    return 345.0 * math.log10((8.0 / 60.0) * t_sec + 1.0) + T0

def calc_section_factor(perimeter, area):
    """
    Рассчитывает приведенную толщину металла (или коэффициент сечения).
    В методике часто используется A/P (м) или P/A (1/м).
    Здесь вернем A/P в мм (приведенная толщина).
    """
    if perimeter <= 0: return 0
    return area / perimeter

def calc_heated_perimeter_ibeam(h, b, tw, tf, exposure="4_sides"):
    """
    Расчет обогреваемого периметра для двутавра (Таблица 4.2).
    exposure: "4_sides" (все стороны) или "3_sides" (частичный обогрев, одна полка закрыта)
    """
    if exposure == "4_sides":
        # 2h + 4b - 2tw
        return 2 * h + 4 * b - 2 * tw
    elif exposure == "3_sides":
        # 2h + 3b - 2tw
        return 2 * h + 3 * b - 2 * tw
    return 2 * h + 4 * b - 2 * tw

def calc_heated_perimeter_rect_tube(h, b, exposure="4_sides"):
    """
    Расчет обогреваемого периметра для прямоугольной трубы (Таблица 4.2).
    exposure: "4_sides" или "3_sides" (верхняя грань шириной b закрыта)
    """
    if exposure == "4_sides":
        # 2h + 2b
        return 2 * (h + b)
    elif exposure == "3_sides":
        # 2h + 2b - b = 2h + b 
        # Таблица: Сечение обогреваемые по всему периметру A/(2h+2b).
        # Сечения при частичном обогреве A/(2h+b). Значит периметр = 2h + b.
        return 2 * h + b
    return 2 * (h + b)

def calc_heated_perimeter_channel(h, b, tw, tf, exposure="4_sides"):
    """
    Расчет обогреваемого периметра для швеллера.
    Принимаем аналогично двутавру (контур):
    4 стороны: 2h + 4b - 2tw
    3 стороны (стенка примыкает): 4 стороны - h
    """
    p_total = 2 * h + 4 * b - 2 * tw
    
    if exposure == "4_sides":
        return p_total
    elif exposure == "3_sides":
        # Частичный обогрев (примыкание полкой, аналогично двутавру).
        # Формула как у двутавра: 2h + 3b - 2tw
        return 2 * h + 3 * b - 2 * tw
    return p_total

def calc_heated_perimeter_circ_tube(d, exposure="4_sides"):
    """
    Расчет обогреваемого периметра для круглой трубы (Таблица 4.2).
    exposure: для трубы обычно только "4_sides" в таблице (нижний ряд).
    П = pi * d
    """
    return math.pi * d
    
def calc_steel_temperature_step_custom(t_steel_prev_k, t_gas_current_k, dt_sec, Am_V):
    """
    Calculates steel temperature using the user-provided algorithm.
    All inputs and calculation in Kelvin.
    
    Args:
        t_steel_prev_k: Previous steel temperature in Kelvin.
        t_gas_current_k: Current gas temperature in Kelvin.
        dt_sec: Time step in seconds.
        Am_V: Section factor 1/m.
        
    Returns:
        New steel temperature in Kelvin.
    """
    
    # Constants from user request
    rho_s = 7800.0  # kg/m3 (Updated to 7800)
    S_pr = 0.563    # Reduced emissivity (Specified by user)
    C_st = 310.0    # J/(kg*K) (Specified by user)
    D_st = 0.48     # (Specified by user)
    
    # Reduced thickness delta_np (m).
    # Am_V is P/A (1/m). delta_pr = A/P = 1/Am_V
    if Am_V <= 0: return t_steel_prev_k
    delta_pr_m = 1.0 / Am_V
    
    Ts_K = t_steel_prev_k
    Tg_K = t_gas_current_k
    
    # 1. Calculate Alpha
    # alpha = 29 + 5.67 * S_pr * ((Tg/100)^4 - (Ts/100)^4) / (Tg - Ts)
    
    diff_temp = Tg_K - Ts_K
    
    if abs(diff_temp) < 0.1:
        alpha = 29.0
    else:
        Tg_K100 = Tg_K / 100.0
        Ts_K100 = Ts_K / 100.0
        
        rad_term = (Tg_K100**4 - Ts_K100**4) / diff_temp
        alpha = 29.0 + 5.67 * S_pr * rad_term
        
    # 2. Specific Heat
    # C_st + D_st * T_st
    # Assuming T_st is in Kelvin based on context of other params being K
    c_s_current = C_st + D_st * Ts_K
    
    # 3. Main Update Formula
    # T_new = [ dt / (rho * delta * C_current) ] * alpha * (Tg - Ts) + Ts
    
    numerator = dt_sec * alpha * diff_temp
    denominator = rho_s * delta_pr_m * c_s_current
    
    if denominator == 0:
         delta_t = 0
    else:
         delta_t = numerator / denominator
    
    return Ts_K + delta_t, alpha

def calculate_fire_resistance(
    Am_V, # P/A in 1/m
    crit_temp, # Celsius
    protection_type="unprotected",
    prot_lambda=None, 
    prot_thickness_mm=0,
    time_step_sec=None, # Ignored, fixed to 1 sec
    max_time_min=60
):
    """
    Simulates heating using the specific user algorithm with 1 sec step.
    Everything internal in Kelvin.
    """
    import pandas as pd
    
    times = []
    temps_gas_c = []
    temps_steel_c = []
    alphas = []
    
    # Initial conditions in Kelvin
    T0_K = 293.0
    t_current_steel_k = T0_K
    
    t_sec = 0.0
    dt_sec = 1.0 # Fixed step 1 sec
    
    max_time_min = float(max_time_min)
    max_time_sec = max_time_min * 60.0
    
    # Arrays for history
    times.append(0.0)
    # Initial gas temp approx T0
    temps_gas_c.append(T0_K - 273.15)
    temps_steel_c.append(t_current_steel_k - 273.15)
    alphas.append(0.0) # Initial alpha placeholder
    
    reached_crit = False
    fire_resistance_time = max_time_min
    
    # Convert crit temp to K for comparison
    crit_temp_k = crit_temp + 273.15
    
    step_count = int(max_time_sec / dt_sec)
    
    for _ in range(step_count):
        # Update time
        t_next_sec = t_sec + dt_sec
        t_next_min = t_next_sec / 60.0
        
        # Get standard fire temp in Kelvin at current step (tau) for alpha calculation?
        # User formula says alpha_tau (at current step) using T_g_tau.
        # So we use T_gas at t_next_sec.
        
        t_gas_next_k = standard_fire_curve(t_next_sec)
        
        # Calculate steel temp for next step
        # T_st,tau = ... using T_st,tau-dtau (prev) and T_g,tau (current/next)
        t_next_steel_k, current_alpha = calc_steel_temperature_step_custom(
            t_current_steel_k, 
            t_gas_next_k, 
            dt_sec, 
            Am_V
        )
        
        # Record
        t_sec = t_next_sec
        t_current_steel_k = t_next_steel_k
        
        times.append(t_next_min)
        temps_gas_c.append(t_gas_next_k - 273.15)
        temps_steel_c.append(t_current_steel_k - 273.15)
        alphas.append(current_alpha)
        
        # Check critical (Compare K)
        if not reached_crit and t_current_steel_k >= crit_temp_k:
            fire_resistance_time = t_next_min
            reached_crit = True
            
    return {
        "R_min": fire_resistance_time if reached_crit else f">{max_time_min:.0f}",
        "raw_time": fire_resistance_time,
        "history": pd.DataFrame({
            "Time_min": times,
            "Time_sec": [t * 60 for t in times],
            "T_gas": temps_gas_c,
            "T_steel": temps_steel_c,
            "Alpha": alphas
        })
    }
