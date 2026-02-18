# 1. Start with a lightweight version of Python
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your Django project files into the container
COPY . .

# 5. Open port 8000 so the outside world can talk to Django
EXPOSE 8000

# 6. The command to start the server when the container runs
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]