FROM python:3.6-alpine

RUN apk --no-cache add \
    python3 \
    git \
    libpq \
    wget \
    ca-certificates \
    python3-dev \
    postgresql-dev \
    build-base \
    libxml2-dev \
    libxslt-dev \
    libstdc++ \
    bash \
    curl
RUN update-ca-certificates

WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt

# ADD repos/os-api-cache repos/os-api-cache
# RUN pip install -e repos/os-api-cache

# ADD repos/os-package-registry repos/os-package-registry
# RUN pip install -e repos/os-package-registry

COPY docker/entrypoint.sh /entrypoint.sh

ADD . .

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["-t 120", "-w 4", "os_api.app:app", "-b 0.0.0.0:8000"]
