# Same Python line used in the local tests
FROM python:3.14-slim

# No .pyc files, and logs appear immediately in the terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the dependency list first, so Docker can cache the install step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the project code (.dockerignore keeps .env and tests out)
COPY . .

# Do not run the API as root inside the container
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# 0.0.0.0 makes the API reachable from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]