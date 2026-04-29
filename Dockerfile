FROM python:3.14
# Creating working directory within the container
WORKDIR /app
# Copying the requirements file to the working directory
COPY requirements.txt .

# Installing dependancies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Setting environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["python", "app.py"]