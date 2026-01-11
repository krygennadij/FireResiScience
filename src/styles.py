"""
Модуль стилей для приложения FireResiScience.
Содержит CSS-стили для улучшения внешнего вида Streamlit-интерфейса.
"""


def get_custom_css():
    """
    Возвращает CSS-стили для приложения.

    Returns:
        str: HTML-строка со стилями для вставки через st.markdown()
    """
    return """
    <style>
    /* Улучшенные заголовки expander */
    .streamlit-expanderHeader {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #1f77b4 !important;
        background-color: #f8f9fa !important;
        border-radius: 5px !important;
        padding: 0.5rem !important;
    }

    /* Кнопки с градиентом */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%);
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }

    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }

    /* Метрики с красивыми рамками */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #555;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #FF4B4B;
    }

    /* Улучшенные tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #ffffff;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #fee;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: 600;
    }

    /* Красивые разделители */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #f0f2f6;
    }

    /* Улучшенные контейнеры */
    [data-testid="stContainer"] {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        background-color: #fafafa;
    }

    /* Toggle switches */
    [data-baseweb="toggle"] {
        background-color: #FF4B4B !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #FF4B4B !important;
    }

    /* Заголовок приложения */
    h1 {
        color: #262730;
        padding-bottom: 1rem;
        border-bottom: 3px solid #FF4B4B;
        margin-bottom: 2rem;
    }

    /* Sidebar улучшения */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }

    /* Pills (выбор типа нагрузки) */
    [data-baseweb="segmented-control"] {
        border-radius: 10px;
        padding: 4px;
        background-color: #f0f2f6;
    }
    </style>
    """
