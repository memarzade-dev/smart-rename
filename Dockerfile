FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY smart_rename_pro.py .

ENTRYPOINT ["python", "smart_rename_pro.py"]
CMD ["--help"] 