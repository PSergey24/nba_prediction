FROM python:3.8 as build_image

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

FROM python:3.8-slim as run_image
ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH="/app"
WORKDIR /app

COPY --from=build_image /opt/venv /opt/venv
COPY --from=build_image /app /app
