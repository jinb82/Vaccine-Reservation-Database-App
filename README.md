# Vaccine Reservation Database App

## Overview
This is a command-line application for scheduling vaccination appointments. The application is hosted on Microsoft Azure, ensuring secure data transactions and user authentication.

## Features
- Schedule vaccination appointments
- User authentication
- Scalable relational database with SQL
- Efficiently handles up to 10,000 concurrent users

## Setup

### Prerequisites
- Python 3.8 or higher
- Anaconda
- Microsoft Azure account

### Steps

1. **Clone the repository:**
    ```bash
    git clone https://github.com/jinb82/Vaccine-Reservation-Database-App.git
    cd Vaccine-Reservation-Database-App
    ```

2. **Set up the environment:**
    - Install Anaconda and create a development environment:
        ```bash
        conda create -n vaccine-reservation python=3.8
        conda activate vaccine-reservation
        conda install pymssql
        ```

3. **Configure the database connection:**
    - Set up the environment variables for your Azure database credentials:
        ```bash
        conda env config vars set Server=YOUR_SERVER
        conda env config vars set DBName=YOUR_DBNAME
        conda env config vars set UserID=YOUR_USERID
        conda env config vars set Password=YOUR_PASSWORD
        conda activate vaccine-reservation
        ```

4. **Initialize the database:**
    - Navigate to the `src/main/resources` directory and run the `create.sql` script to set up the database schema.
        ```bash
        cd src/main/resources
        python create.sql
        ```

5. **Run the application:**
    ```bash
    python src/main/scheduler/Scheduler.py
    ```

## Usage

### Commands
- `create_patient <username> <password>`
  - Print "Created user <username>" if creation is successful.
  - Print "Username taken, try again" if the username is already taken.
  - For all other errors, print "Create patient failed".

- `create_caregiver <username> <password>`
  - Print "Created user <username>" if creation is successful.
  - Print "Username taken, try again" if the username is already taken.
  - For all other errors, print "Create caregiver failed".

- `login_patient <username> <password>`
  - Print "Logged in as <username>" if login is successful.
  - Print "User already logged in, try again" if a user is already logged in.
  - For all other errors, print "Login patient failed".

- `login_caregiver <username> <password>`
  - Print "Logged in as <username>" if login is successful.
  - Print "User already logged in, try again" if a user is already logged in.
  - For all other errors, print "Login caregiver failed".

- `search_caregiver_schedule <date>`
  - Print the username of available caregivers and the available vaccines and their doses for the given date.
  - Print "Please login first" if no user is logged in.
  - For all other errors, print "Please try again".

- `reserve <date> <vaccine>`
  - Reserve an appointment for the logged-in patient.
  - Print "Appointment ID {appointment_id} Caregiver username {username}" if successful.
  - Print "No caregiver is available" if no caregivers are available.
  - Print "Not enough available doses" if there are not enough vaccine doses.
  - Print "Please login first" if no user is logged in.
  - Print "Please login as a patient" if the logged-in user is not a patient.
  - For all other errors, print "Please try again".

- `show_appointments`
  - Print the scheduled appointments for the logged-in user.
  - Print "Please login first" if no user is logged in.
  - For all other errors, print "Please try again".

- `logout`
  - Print "Successfully logged out" if the user is logged out.
  - Print "Please login first" if no user is logged in.
  - For all other errors, print "Please try again".

- `quit`
  - Exit the application.

## Additional Information
- This project uses salting and hashing for password security.
- The database schema includes Patients, Caregivers, and Vaccines tables.
- The application logic is implemented in Python using the `pymssql` library to interact with the Azure SQL database.

