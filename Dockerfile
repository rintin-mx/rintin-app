FROM python:3.11-bullseye
LABEL authors="diogenes"


COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]