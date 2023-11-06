# Use the official Python 3.8 image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /server

# Copy your Flask application script and its dependencies
COPY . /server

# Install Flask and other dependencies if needed
RUN pip install -r requirements.txt
# Expose the port that your Flask app will run on
EXPOSE 1234

# Command to run the Flask application
CMD [ "sh", "-c", "FLASK_APP=/server/standalone.py FLASK_DEBUG=True python3 -m flask run --host 0.0.0.0 --port 1234 --with-threads" ]

