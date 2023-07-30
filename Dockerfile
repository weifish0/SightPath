FROM python:3.9-slim-buster

# Define WORKDIR
WORKDIR /app

# Copy all files from current directory to WORKDIR
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run database migrations
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate 

# Expose port 8000
EXPOSE 8000

# Run the application
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]