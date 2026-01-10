
# Таблица Б.1 — Температурные коэффициенты снижения механических свойств строительных сталей
# Формат: {температура: коэффициент}

# Температурный коэффициент снижения модуля упругости (gamma_e)
# Для всех сталей (упрощенно, так как они близки, или можно разделить если критично)
GAMMA_E_DATA = {
    20: 1.00,
    100: 1.00, # Предположение для интерполяции
    250: 1.00,
    300: 0.94, # C235-C255
    350: 0.89,
    400: 0.84,
    450: 0.79,
    500: 0.73,
    550: 0.67,
    600: 0.59,
    650: 0.52,
    700: 0.43,
    800: 0.20 # Примерное значение для экстраполяции
}

# Температурный коэффициент снижения прочности (gamma_T)
# Разделение по группам прочности

# Стали обычной прочности (С235, С245, С255)
GAMMA_T_NORMAL_STRENGTH = {
    20: 1.00,
    100: 1.00,
    250: 1.00,
    300: 0.84,
    350: 0.78,
    400: 0.72,
    450: 0.67,
    500: 0.61,
    550: 0.54,
    600: 0.45,
    650: 0.34,
    700: 0.20,
    800: 0.00 # Теоретически 0 при плавлении/высоких Т
}

# Стали повышенной прочности (С345, С345К, С355, С375)
GAMMA_T_INCREASED_STRENGTH = {
    20: 1.00,
    100: 1.00,
    250: 1.00,
    300: 0.84,
    350: 0.75,
    400: 0.70,
    450: 0.65,
    500: 0.60,
    550: 0.55,
    600: 0.46,
    650: 0.34,
    700: 0.18,
    800: 0.00
}

# Стали высокой прочности (С390, С440, С550, С590)
GAMMA_T_HIGH_STRENGTH = {
    20: 1.00,
    100: 1.00,
    250: 1.00,
    300: 0.89,
    350: 0.83,
    400: 0.79,
    450: 0.75,
    500: 0.71,
    550: 0.66,
    600: 0.58,
    650: 0.47,
    700: 0.32,
    800: 0.00
}

def get_gamma_t_table(steel_grade: str):
    """Возвращает соответствующую таблицу gamma_t в зависимости от марки стали."""
    # Упрощенная логика определения группы прочности
    # В реальном проекте лучше иметь полный список марок
    grade = steel_grade.upper()
    if any(x in grade for x in ['C390', 'С390', 'C440', 'С440', 'C550', 'С550', 'C590', 'С590']):
        return GAMMA_T_HIGH_STRENGTH
    elif any(x in grade for x in ['C345', 'С345', 'C355', 'С355', 'C375', 'С375']):
        return GAMMA_T_INCREASED_STRENGTH
    else:
        # По умолчанию обычная прочность (C235, C245, C255 и др.)
        return GAMMA_T_NORMAL_STRENGTH

def interpolate(x, x1, y1, x2, y2):
    """Линейная интерполяция."""
    if x2 == x1: return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

def get_critical_temp(gamma_t_target, steel_grade: str) -> float:
    """
    Определяет критическую температуру для заданного коэффициента снижения прочности gamma_t.
    Использует обратную интерполяцию по таблице Б.1.
    """
    table = get_gamma_t_table(steel_grade)
    
    # Сортируем температуры по возрастанию (они уже отсортированы в dict, но для надежности)
    temps = sorted(table.keys())
    
    # gamma_t падает с ростом температуры.
    # Нам нужно найти интервал, где table[t1] >= gamma_t_target >= table[t2]
    
    # Граничные случаи
    if gamma_t_target >= 1.0:
        return {"value": 20.0, "trace": None}
    if gamma_t_target <= table[temps[-1]]:
        return {"value": temps[-1], "trace": None}

    for i in range(len(temps) - 1):
        t1 = temps[i]
        t2 = temps[i+1]
        g1 = table[t1]
        g2 = table[t2]
        
        # Проверяем попадание в интервал (учитывая убывание gamma_t)
        if g1 >= gamma_t_target >= g2:
            # Обратная интерполяция: находим T для заданного gamma
            # g(t) ~ линейно. t = t1 + (g_target - g1) * (t2 - t1) / (g2 - g1)
            t_cr = t1
            if g1 != g2:
                 t_cr = t1 + (gamma_t_target - g1) * (t2 - t1) / (g2 - g1)
            
            return {
                "value": t_cr,
                "trace": {"t1": t1, "g1": g1, "t2": t2, "g2": g2}
            }
            
    return {"value": temps[-1], "trace": None}

# Таблица Б.7 — Нормативные сопротивления Ryn (СП 16.13330.2017)
# structure: Grade -> List of (max_thickness, Ryn_value)
# Ordered by thickness ascending (or logic to check ranges)
RYN_TABLE = {
    "C245": [
        (20, 245),
        (40, 235)
    ],
    "C255": [
        (10, 255),
        (20, 245),
        (40, 235)
    ],
    "C345": [
        (10, 345),
        (20, 325),
        (40, 305)
    ],
    "C345K": [
        (10, 345) 
         # Table image says only 4-10. What if >10? Assuming limited range or fallback.
         # Provided image only shows up to 10 for C345K.
    ],
    "C355": [
        (16, 355),
        (40, 345)
    ],
    "C355-1": [
        (16, 355),
        (40, 345)
    ],
    "C390": [
        (10, 390),
        (20, 380),
        (40, 370)
    ],
    # Adding C235 for completeness if needed (usually 235 flat or similar to C245?)
    # Image doesn't show C235. Standard usually 235 for t<=20.
    "C235": [
         (20, 235),
         (40, 225) # Estimation based on common decrease
    ]
}

def get_ryn(steel_grade: str, thickness_mm: float) -> float:
    """
    Возвращает нормативное сопротивление Ryn (МПа) в зависимости от марки стали и толщины.
    Для фасонного проката за толщину принимается толщина полки.
    """
    grade = steel_grade.upper()
    
    # Fallback if grade not found
    if grade not in RYN_TABLE:
        # Try to parse number from string, e.g. "C245" -> 245
        # Simplistic fallback
        try:
             val = float(''.join(filter(str.isdigit, grade)))
             return val
        except:
             return 245.0
             
    data = RYN_TABLE[grade]
    
    # Find bucket
    # Table usually "From X to Y inclusive"
    # Our data structure: (limit, value). If t <= limit -> value.
    # Assuming the list is sorted by thickness.
    
    for limit, val in data:
        if thickness_mm <= limit:
            return float(val)
            
    # If thickness exceeds max in table, usually take the last value or warn.
    # We will return the last value (for thickest valid range)
    return float(data[-1][1])
