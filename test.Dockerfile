ARG PYTHON_VERSION=3.6.3
FROM python:${PYTHON_VERSION}-alpine
WORKDIR /app
RUN apk add --no-cache\
    curl\
    git\
    # Bash and general build packages
    bash make gcc musl-dev linux-headers\
    # For CFFI support
    libffi-dev\
    # For cairosvg
    cairo-dev\
    # For lxml
    libxml2-dev libxslt-dev\
    # PIL/Pillow support
    zlib-dev jpeg-dev libwebp-dev freetype-dev lcms2-dev openjpeg-dev\
    # For moto (tests)
    openssl-dev
COPY test.docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
COPY setup.py /app
RUN pip install -e .[full,test,test_s3] flake8 isort
COPY conftest.py /app
COPY flask_resize /app/flask_resize
COPY tests /app/tests
RUN pip install -e .
ENTRYPOINT ["/docker-entrypoint.sh"]
