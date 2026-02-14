# User Details Application

This is a Flask-based web application for registering and filtering user details. The application includes a frontend for user interaction and a backend for handling database operations.

## Features
- User registration with fields: name, age, sex, mobile number, experience, and locality.
- Filtering users based on name, age, sex, and locality.

## Setup Instructions

### Prerequisites
- Docker installed on your system.

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd user-details
   ```

2. Build the Docker image:
   ```bash
   docker build -t user-details-app .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 5000:5000 user-details-app
   ```

4. Open the application in your browser at `http://localhost:5000`.

## File Structure
- `app.py`: Main application file.
- `templates/index.html`: Frontend HTML file.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Docker configuration.
- `.flaskenv`: Flask environment variables.

## License
This project is licensed under the MIT License.