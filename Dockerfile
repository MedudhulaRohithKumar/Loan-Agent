FROM python:3.10-slim

WORKDIR /app

# Ensure we don't write generic standard output to disk unnecessarily
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install default dependencies (you can replace this with copying a requirements.txt)
RUN pip install --no-cache-dir fastapi uvicorn python-multipart joblib scikit-learn==1.7.2 pandas pydantic

# Copy the entire project to the working directory
COPY . /app/

# Expose the API port
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
