# Use Alpine Linux as base to minimize image size
FROM python:3.12-alpine

# Create a non-root user for security
RUN adduser -D robominder

# Set working directory
WORKDIR /app

# Copy only the required file
COPY bot.py /app/bot.py

# Install only the required dependency
# Use --no-cache to avoid storing package index
# Use virtual environment to keep dependencies isolated
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir slixmpp && \
    chmod +x /app/bot.py && \
    chown -R robominder:robominder /app

# Switch to non-root user
USER robominder

# Use virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Run the bot
CMD ["python", "bot.py"]