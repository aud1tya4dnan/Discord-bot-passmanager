# Menggunakan base image Python 3.9
FROM python:3.9-slim-buster

# Mengatur working directory
WORKDIR /app

# Menyalin dependencies file ke container
COPY requirements.txt .

# Menginstal dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin kode bot ke container
COPY . .

# Menjalankan bot Discord saat container dijalankan
CMD ["python", "newgpt.py"]
