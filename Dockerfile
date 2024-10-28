FROM python:3.12-alpine

RUN adduser -D robominder

WORKDIR /app

COPY bot.py /app/bot.py

RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir slixmpp && \
    chmod +x /app/bot.py && \
    chown -R robominder:robominder /app

USER robominder

ENV PATH="/app/venv/bin:$PATH"

CMD ["python", "bot.py"]