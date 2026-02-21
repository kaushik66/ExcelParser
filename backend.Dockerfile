FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
# We can just copy everything from the root directory into /app (which includes the frontend folder, 
# but it's better to ignore it or just let it exist)
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the uvicorn API server on all network interfaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
