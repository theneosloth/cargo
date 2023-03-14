FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry
RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "hunting_hawk.web.main:app", "--host", "0.0.0.0", "--port", "8080"]
