# Dockerfile
# Use a Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script
COPY telegram_bot.py .

# Command to run the bot. We use polling here since webhook setup is complex.
# Note: For professional Cloud Run deployment, you should use Webhooks, 
# but polling is simpler for a private project.
CMD ["python", "telegram_bot.py"]
