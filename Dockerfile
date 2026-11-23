FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system agentqual && useradd --system --gid agentqual --home-dir /app agentqual
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=agentqual:agentqual app ./app
COPY --chown=agentqual:agentqual data ./data
USER agentqual
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3)"
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
