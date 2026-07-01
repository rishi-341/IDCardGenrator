# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# System packages: libzbar0 for pyzbar, libgl1 for Pillow, gcc for any C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
        libzbar0 \
        libzbar-dev \
        libglib2.0-0 \
        libgl1 \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project source ───────────────────────────────────────────────────────
COPY . .

# ── Runtime directories ───────────────────────────────────────────────────────
RUN mkdir -p media/sessions media/uploads barcode staticfiles

# ── Collect static files ──────────────────────────────────────────────────────
# Use a dummy SECRET_KEY so Django doesn't complain during build.
# WhiteNoise storage is used so the manifest is baked into the image.
RUN SECRET_KEY=build-only-dummy-key \
    DJANGO_SETTINGS_MODULE=idcardweb.settings \
    python manage.py collectstatic --noinput

# ── Port ──────────────────────────────────────────────────────────────────────
# Render injects $PORT at runtime — we read it in CMD below.
# EXPOSE is informational only.
EXPOSE 8000

# ── Start ─────────────────────────────────────────────────────────────────────
# Use shell form so $PORT is expanded at container start time.
# 1 worker keeps memory under Render free-tier limit (512 MB).
# 120 s timeout covers large PDF generation batches.
CMD gunicorn idcardweb.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120 \
    --log-level info
