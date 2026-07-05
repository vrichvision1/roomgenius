FROM python:3.11-slim

WORKDIR /app

# ติดตั้ง System dependencies ที่อาจจำเป็นสำหรับ asyncpg หรืองานอื่นๆ
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกและติดตั้ง Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกซอร์สโค้ด
COPY . .

# กำหนดโฟลเดอร์สำหรับเก็บข้อมูลถาวร
RUN mkdir -p /data/conversations /data/artifacts

EXPOSE 8765

CMD ["python", "main.py"]
