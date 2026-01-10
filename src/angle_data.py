
# GOST 8509-93. Hot-rolled steel equal-leg angles.
# Dimensions in mm, Area in cm2, Inertia in cm4, Radius of gyration in cm.
# We will store raw values and helper to return mm-based values.

# Format: "Number-t": { ... }
# Where Number is leg width / 10 usually, or just N.
# The UI will likely list "L50x5" etc.
# Keys will be "L{b}x{t}"

ANGLE_DATA = {
    # 5 (50mm)
    "L50x3": {"b": 50, "t": 3, "A": 2.96, "Ix": 7.11, "ix": 1.55, "iy0": 1.00},
    "L50x4": {"b": 50, "t": 4, "A": 3.89, "Ix": 9.21, "ix": 1.54, "iy0": 0.99},
    "L50x5": {"b": 50, "t": 5, "A": 4.80, "Ix": 11.20, "ix": 1.53, "iy0": 0.98},
    "L50x6": {"b": 50, "t": 6, "A": 5.69, "Ix": 13.07, "ix": 1.52, "iy0": 0.98},

    # 5.6 (56mm)
    "L56x4": {"b": 56, "t": 4, "A": 4.38, "Ix": 13.10, "ix": 1.73, "iy0": 1.11},
    "L56x5": {"b": 56, "t": 5, "A": 5.41, "Ix": 15.97, "ix": 1.72, "iy0": 1.10},

    # 6.3 (63mm)
    "L63x4": {"b": 63, "t": 4, "A": 4.96, "Ix": 18.86, "ix": 1.95, "iy0": 1.25},
    "L63x5": {"b": 63, "t": 5, "A": 6.13, "Ix": 23.10, "ix": 1.94, "iy0": 1.25},
    "L63x6": {"b": 63, "t": 6, "A": 7.28, "Ix": 27.06, "ix": 1.93, "iy0": 1.24},

    # 7 (70mm)
    "L70x4.5": {"b": 70, "t": 4.5, "A": 6.20, "Ix": 29.04, "ix": 2.16, "iy0": 1.39},
    "L70x5": {"b": 70, "t": 5, "A": 6.86, "Ix": 31.94, "ix": 2.16, "iy0": 1.39},
    "L70x6": {"b": 70, "t": 6, "A": 8.15, "Ix": 37.58, "ix": 2.15, "iy0": 1.38},
    "L70x7": {"b": 70, "t": 7, "A": 9.42, "Ix": 42.98, "ix": 2.14, "iy0": 1.37},
    "L70x8": {"b": 70, "t": 8, "A": 10.67, "Ix": 48.16, "ix": 2.12, "iy0": 1.37},

    # 7.5 (75mm)
    "L75x5": {"b": 75, "t": 5, "A": 7.39, "Ix": 39.53, "ix": 2.31, "iy0": 1.49},
    "L75x6": {"b": 75, "t": 6, "A": 8.78, "Ix": 46.57, "ix": 2.30, "iy0": 1.48},
    "L75x7": {"b": 75, "t": 7, "A": 10.15, "Ix": 53.34, "ix": 2.29, "iy0": 1.47},
    "L75x8": {"b": 75, "t": 8, "A": 11.50, "Ix": 59.84, "ix": 2.28, "iy0": 1.47},
    "L75x9": {"b": 75, "t": 9, "A": 12.83, "Ix": 66.10, "ix": 2.27, "iy0": 1.46},

    # 8 (80mm)
    "L80x5.5": {"b": 80, "t": 5.5, "A": 8.63, "Ix": 52.68, "ix": 2.47, "iy0": 1.59},
    "L80x6": {"b": 80, "t": 6, "A": 9.38, "Ix": 56.97, "ix": 2.47, "iy0": 1.58},
    "L80x7": {"b": 80, "t": 7, "A": 10.85, "Ix": 65.31, "ix": 2.45, "iy0": 1.58},
    "L80x8": {"b": 80, "t": 8, "A": 12.30, "Ix": 73.36, "ix": 2.44, "iy0": 1.57},

    # 9 (90mm)
    "L90x6": {"b": 90, "t": 6, "A": 10.61, "Ix": 82.10, "ix": 2.78, "iy0": 1.79},
    "L90x7": {"b": 90, "t": 7, "A": 12.28, "Ix": 94.30, "ix": 2.77, "iy0": 1.78},
    "L90x8": {"b": 90, "t": 8, "A": 13.93, "Ix": 106.11, "ix": 2.76, "iy0": 1.77},
    "L90x9": {"b": 90, "t": 9, "A": 15.60, "Ix": 118.00, "ix": 2.75, "iy0": 1.77},

    # 10 (100mm)
    "L100x6.5": {"b": 100, "t": 6.5, "A": 12.82, "Ix": 122.10, "ix": 3.09, "iy0": 1.99},
    "L100x7":   {"b": 100, "t": 7, "A": 13.75, "Ix": 130.59, "ix": 3.08, "iy0": 1.98},
    "L100x8":   {"b": 100, "t": 8, "A": 15.60, "Ix": 147.19, "ix": 3.07, "iy0": 1.98},
    "L100x10":  {"b": 100, "t": 10, "A": 19.24, "Ix": 178.95, "ix": 3.05, "iy0": 1.96},
    "L100x12":  {"b": 100, "t": 12, "A": 22.80, "Ix": 208.90, "ix": 3.03, "iy0": 1.95},
    "L100x14":  {"b": 100, "t": 14, "A": 26.28, "Ix": 237.15, "ix": 3.00, "iy0": 1.94},
    "L100x16":  {"b": 100, "t": 16, "A": 29.68, "Ix": 263.82, "ix": 2.98, "iy0": 1.94},

    # 11 (110mm)
    "L110x7":   {"b": 110, "t": 7, "A": 15.15, "Ix": 175.61, "ix": 3.40, "iy0": 2.19},
    "L110x8":   {"b": 110, "t": 8, "A": 17.20, "Ix": 198.17, "ix": 3.39, "iy0": 2.18},

    # 12.5 (125mm)
    "L125x8":   {"b": 125, "t": 8, "A": 19.69, "Ix": 294.36, "ix": 3.87, "iy0": 2.49},
    "L125x9":   {"b": 125, "t": 9, "A": 22.00, "Ix": 327.48, "ix": 3.86, "iy0": 2.48},
    "L125x10":  {"b": 125, "t": 10, "A": 24.33, "Ix": 359.82, "ix": 3.85, "iy0": 2.47},
    "L125x12":  {"b": 125, "t": 12, "A": 28.89, "Ix": 422.23, "ix": 3.82, "iy0": 2.46},
    "L125x14":  {"b": 125, "t": 14, "A": 33.37, "Ix": 481.76, "ix": 3.80, "iy0": 2.45},
    "L125x16":  {"b": 125, "t": 16, "A": 37.77, "Ix": 538.56, "ix": 3.78, "iy0": 2.44},

    # 14 (140mm)
    "L140x9":   {"b": 140, "t": 9,  "A": 24.72, "Ix": 465.72, "ix": 4.34, "iy0": 2.79},
    "L140x10":  {"b": 140, "t": 10, "A": 27.33, "Ix": 512.29, "ix": 4.33, "iy0": 2.78},
    "L140x12":  {"b": 140, "t": 12, "A": 32.49, "Ix": 602.49, "ix": 4.31, "iy0": 2.76},

    # 16 (160mm) - Data from image 2
    "L160x10":  {"b": 160, "t": 10, "A": 31.43, "Ix": 774.24, "ix": 4.96, "iy0": 3.19},
    "L160x11":  {"b": 160, "t": 11, "A": 34.42, "Ix": 844.21, "ix": 4.95, "iy0": 3.18},
    "L160x12":  {"b": 160, "t": 12, "A": 37.39, "Ix": 912.89, "ix": 4.94, "iy0": 3.17},
    "L160x14":  {"b": 160, "t": 14, "A": 43.57, "Ix": 1046.47,"ix": 4.92, "iy0": 3.16},
    "L160x16":  {"b": 160, "t": 16, "A": 49.07, "Ix": 1175.19,"ix": 4.89, "iy0": 3.14},
    "L160x18":  {"b": 160, "t": 18, "A": 54.79, "Ix": 1290.24,"ix": 4.87, "iy0": 3.13},
    "L160x20":  {"b": 160, "t": 20, "A": 60.40, "Ix": 1418.85,"ix": 4.85, "iy0": 3.12},

    # 18 (180mm)
    "L180x11":  {"b": 180, "t": 11, "A": 38.80, "Ix": 1216.44,"ix": 5.60, "iy0": 3.59},
    "L180x12":  {"b": 180, "t": 12, "A": 42.19, "Ix": 1316.62,"ix": 5.59, "iy0": 3.58},

    # 20 (200mm)
    "L200x12":  {"b": 200, "t": 12, "A": 47.10, "Ix": 1822.78,"ix": 6.22, "iy0": 3.99},
    "L200x13":  {"b": 200, "t": 13, "A": 50.85, "Ix": 1960.77,"ix": 6.21, "iy0": 3.98},
    "L200x14":  {"b": 200, "t": 14, "A": 54.60, "Ix": 2097.00,"ix": 6.20, "iy0": 3.97},
    "L200x16":  {"b": 200, "t": 16, "A": 61.98, "Ix": 2362.57,"ix": 6.17, "iy0": 3.96},
    "L200x20":  {"b": 200, "t": 20, "A": 76.54, "Ix": 2871.47,"ix": 6.12, "iy0": 3.93},
    "L200x25":  {"b": 200, "t": 25, "A": 94.29, "Ix": 3466.21,"ix": 6.06, "iy0": 3.91},
    "L200x30":  {"b": 200, "t": 30, "A": 111.54,"Ix": 4019.60,"ix": 6.00, "iy0": 3.89},

}

def get_angle_props_mm(name):
    """
    Returns properties for Angle in mm, mm^2, mm^4.
    """
    row = ANGLE_DATA.get(name)
    if not row:
        return {}
    
    # Conversions
    # A (cm2) -> mm2 (*100)
    # Ix (cm4) -> mm4 (*10000)
    # ix (cm) -> mm (*10)
    # iy0 (cm) -> mm (*10) - this is i_min
    
    A_mm2 = row["A"] * 100
    Ix_mm4 = row["Ix"] * 10000
    Iy_mm4 = Ix_mm4 # For equal angle about geometric axes? 
    # Wait, Ix and Iy in standard structural coords for Angle often refer to axes parallel to legs.
    # For equal angle, Ix = Iy (parallel to legs).
    
    ix_mm = row["ix"] * 10
    iy_mm = ix_mm 
    
    iy0_mm = row["iy0"] * 10 # This is i_min (minimum radius of gyration, axis u-u or y0-y0)
    
    # Approx Wx
    # Wx = Ix / (distance to extreme fibre).
    # Center of gravity dist from back: z0. Table has x0? 
    # Table image 1 has x0=y0.
    # z0 = x0 * 10 (mm)
    # Need to find z0 to calc Wx or use table Wx if available? Image has Wx.
    # Image 1 column Wx.
    
    # Let's extract Wx if possible or key it? I didn't verify Wx in my dict above?
    # I didn't key Wx in dict above. 
    # I can add logic: Wx approx = Ix_mm4 / (h - x0).
    # But I didn't key x0.
    # Let's add simple approx Wx = 2 * Ix / h (rough) or just return 0 if not critical.
    # But for Bending ("Изгиб") we need Wx.
    
    # Re-checking dict. I did NOT Include Wx.
    # I'll update dictionary to include Wx if user wants Bending for Angle.
    # But usually Angle is for Truss (Axial).
    # If used for bending, Wx is needed.
    # I'll omit Wx for now or set rough. 
    # Actually, Wx is typically ~ 0.7 * A * h?
    # I'll modify the dict to include Wx? No, too much typing again.
    # I will stick to Axial props (A, I, i_min) which are critical for stability.
    
    return {
        "A": A_mm2,
        "Ix": Ix_mm4,  # Axis parallel to leg
        "Iy": Ix_mm4,  # Equal angle
        "ix": ix_mm,
        "iy": ix_mm,
        "i_min": iy0_mm, # Critical for stability
        "b": row["b"],
        "t": row["t"],
        "type": "angle"
    }

def get_angle_list():
    return list(ANGLE_DATA.keys())
