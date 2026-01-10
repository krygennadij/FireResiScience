# Инструкция по установке Calculation_MK

## Быстрая установка

### 1. Клонирование репозитория (если еще не сделано)

```bash
git clone <repository-url>
cd Calculation_MK
```

### 2. Создание виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Важно!** Если возникает ошибка с `kaleido`, установите его отдельно:

```bash
pip install kaleido
```

### 4. Проверка установки

Проверьте, что все модули установлены:

```bash
python -c "import streamlit; import plotly; import kaleido; print('Все модули установлены успешно!')"
```

### 5. Запуск приложения

```bash
streamlit run app.py
```

Приложение будет доступно по адресу: `http://localhost:8501`

---

## Решение проблем

### Ошибка: "Module 'kaleido' not found"

**Проблема:** Библиотека kaleido необходима для экспорта графиков в изображения (для отчетов DOCX).

**Решение:**

```bash
pip install kaleido
```

Если не помогает, попробуйте:

```bash
pip uninstall kaleido
pip install --upgrade kaleido
```

### Ошибка: "module 'streamlit' has no attribute 'pills'"

**Проблема:** Установлена старая версия Streamlit (< 1.40.0). Компонент st.pills() появился в версии 1.40.0.

**Решение:**

1. Остановите приложение (Ctrl+C)
2. Обновите Streamlit:

```bash
pip install --upgrade streamlit
```

3. Проверьте версию:

```bash
streamlit --version
```

Должна быть версия **1.40.0 или выше**.

4. Перезапустите приложение:

```bash
streamlit run app.py
```

**Если у вас несколько версий Python:** Убедитесь, что обновляете для правильной версии Python:

```bash
python -m pip install --upgrade streamlit
```

### Ошибка: "python-docx not found"

**Проблема:** Неправильно указана зависимость в requirements.txt.

**Решение:**

```bash
pip install python-docx
```

### Ошибка: "Port 8501 is already in use"

**Проблема:** Порт занят другим процессом Streamlit.

**Решение 1:** Остановите предыдущий процесс Streamlit (Ctrl+C)

**Решение 2:** Запустите на другом порту:

```bash
streamlit run app.py --server.port 8502
```

### Ошибка импорта модулей src

**Проблема:** Python не видит модули в папке src.

**Решение:** Убедитесь, что вы запускаете из корневой директории проекта:

```bash
cd Calculation_MK
streamlit run app.py
```

### Проблемы с кодировкой на Windows

**Проблема:** Русские символы отображаются некорректно.

**Решение:** Установите переменную окружения:

```bash
set PYTHONIOENCODING=utf-8
streamlit run app.py
```

Или добавьте в начало app.py:

```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Обновление зависимостей

Если вы обновили код из репозитория:

```bash
pip install --upgrade -r requirements.txt
```

Или обновите только основные пакеты:

```bash
pip install --upgrade streamlit plotly pandas numpy python-docx kaleido
```

---

## Системные требования

### Минимальные:
- Python 3.8+
- **Streamlit 1.40.0+** (для современных UI компонентов: st.pills, st.toggle)
- 2 GB RAM
- 100 MB свободного места на диске

### Рекомендуемые:
- Python 3.9+ или 3.10+
- 4 GB RAM
- 500 MB свободного места

### Поддерживаемые ОС:
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)

---

## Запуск в production

### Для локального использования:

```bash
streamlit run app.py --server.headless true
```

### Для сетевого доступа:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

**⚠️ Внимание:** Не открывайте доступ к приложению в интернет без настройки аутентификации!

### Для deployment на сервер:

Рекомендуется использовать:
- **Streamlit Cloud** (бесплатно для публичных репозиториев)
- **Heroku** с Procfile
- **Docker** с официальным образом Python

Пример Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

---

## Проверка работоспособности

После установки выполните тестовый расчет:

1. Откройте приложение `http://localhost:8501`
2. В боковой панели выберите:
   - Тип сечения: **Двутавр**
   - Стандартный профиль: **I-20**
   - Марка стали: **C245**
   - Тип нагружения: **Центральное сжатие**
   - Продольная сила: **500 кН**
   - Длина: **3 м**
3. Проверьте, что расчет выполняется без ошибок
4. Попробуйте сгенерировать отчет во вкладке "Отчет"

Если все работает - установка прошла успешно! ✅

---

## Контакты и поддержка

При возникновении проблем:

1. Проверьте раздел "Решение проблем" выше
2. Убедитесь, что используете последнюю версию из репозитория
3. Создайте Issue в репозитории с описанием проблемы

**Полезные команды для диагностики:**

```bash
# Проверка версии Python
python --version

# Список установленных пакетов
pip list

# Проверка версии Streamlit
streamlit --version

# Очистка кэша Streamlit
streamlit cache clear
```
