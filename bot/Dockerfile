FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY bot/pyproject.toml ./

RUN uv sync

COPY bot/ ./bot/

CMD ["uv", "run", "python", "bot/bot.py"]