FROM python:3.12.3-slim

WORKDIR /app

# mysqlclient 빌드에 필요한 의존성(목적: WSL/로컬 차이 제거)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    libmariadb-dev \
    ca-certificates \
    curl \
    && update-ca-certificates \
    && curl -fsSL https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /etc/ssl/certs/rds-global-bundle.pem \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
COPY _shared /opt/stagelog-shared
RUN set -eu; \
    if [ -f /opt/stagelog-shared/pyproject.toml ]; then \
      SHARED_PKG_DIR=/opt/stagelog-shared; \
    elif [ -f /opt/stagelog-shared/shared/pyproject.toml ]; then \
      SHARED_PKG_DIR=/opt/stagelog-shared/shared; \
    else \
      echo "shared package root not found under /opt/stagelog-shared" >&2; \
      find /opt/stagelog-shared -maxdepth 2 -type f | sort >&2; \
      exit 1; \
    fi; \
    pip install --upgrade pip && pip install -r requirements.txt && pip install "${SHARED_PKG_DIR}"

# 운영환경을 위해 소스 코드 전체를 이미지 안에 넣기
COPY . /app/
RUN rm -rf /app/_shared

# 소스는 volume mount로 개발(빠른 빌드). 운영에서는 COPY 방식으로 변경
EXPOSE 8000

CMD ["sh", "-lc", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 config.wsgi:application --access-logfile - --error-logfile - --log-level debug --capture-output --timeout 120"]
