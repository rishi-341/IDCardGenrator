# ── Stage 1: base image ───────────────────────────────────────────────────────
FROM python:3.12-slim

# System packages needed by pyzbar (libzbar0) and Pillow / reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
        libzbar0 \
        libzbar-dev \
        libglib2.0-0 \
        libgl1 \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps ───────────────────────────────────────────────────────────────
# Copy requirements first so Docker caches this layer when code-only changes occur
COPY requirements.txt .
RUN pip install -r requirements.txt

# ── Copy project ──────────────────────────────────────────────────────────────
COPY . .

# ── Runtime directories ───────────────────────────────────────────────────────
# media/sessions  – file-based Django sessions
# media/uploads   – uploaded Excel files and extracted photos
# barcode         – barcode PNG files generated at runtime
RUN mkdir -p media/sessions media/uploads barcode staticfiles

# ── Collect static files ──────────────────────────────────────────────────────
RUN python manage.py collectstatic --noinput

# ── Port ──────────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Entrypoint ────────────────────────────────────────────────────────────────
# - 1 worker per Render free-tier container (512 MB RAM)
# - 120 s timeout: PDF generation for large batches can take a while
# - bind 0.0.0.0 so Render's proxy can reach it
CMD ["gunicorn", "idcardweb.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "1", \
     "--timeout", "120", \
     "--log-level", "info"]
