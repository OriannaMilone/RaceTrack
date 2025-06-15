# RaceTrack
This project was developed as part of my Bachelor's Thesis. It consists of a simulation and prediction platform for Formula 1 races, including visualization and scheduling functionalities.

The system is composed of two main modules:

- Backend & Frontend (Node.js): race scheduling, admin panel, simulation control via cron jobs, and real-time WebSocket communication.
- Simulation & Prediction Engine (Python): responsible for running race simulations and generating predictions using machine learning models.

---

## Project Structure
```bash
RaceTrack/
│
├── server.js                -> Main backend server (Node.js)
├── package.json             -> Backend dependencies
├── requirements.txt         -> Python dependencies (simulation & ML models)
├── race_simulator/          -> Simulation logic
├── prediction_model/        -> Machine Learning models and predictors
├── web_project/             -> Static frontend (views, public resources)
├── database/                -> Database scripts 
├── .env                     -> Environment variables (database credentials)
└── etc...
```
---
## 🗄️ Setup Instructions
### 1️⃣ Prerequisites

You need to have **Python** installed locally.

You can download and install Python from:  
https://www.python.org/downloads/

> **Recommended version:** Python 3.12 or higher.

You need to have **Git** installed locally.

You can download and install Git from:  
https://git-scm.com/downloads

> **Recommended version:** Git 2.30 or higher.

You need to have **Node.js** installed locally.

You can download and install Node.js from:  
https://nodejs.org/en/download/

> **Recommended version:** Node.js 18.x or higher.
---


### 1️⃣ Clone the repository
```bash
git clone https://github.com/OriannaMilone/RaceTrack.git
cd RaceTrack
```
### 2️⃣ Install dependencies
#### a) Backend (Node.js)

```bash
npm install
```
#### b) Simulator & Prediction Engine (Python)

It is recommended to use a virtual environment:

##### Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
# Install Python dependencies
```bash
pip install -r requirements.txt
```
---

## 🗄️ Database Setup

### 1️⃣ Prerequisites

You need to have **PostgreSQL** installed locally to run the database.

You can download and install PostgreSQL from:  
https://www.postgresql.org/download/

> **Recommended version:** PostgreSQL 13 or higher (the script is backward compatible).

---

### 2️⃣ Initial Configuration

#### 2.1 Navigate to the SQL script directory

```bash
cd ~/RaceTrack/database/
```

#### 2.2 (Optional, in case of permission issues)
```bash
chmod +r ddbb.sql
```

#### 2.3  Access psql as the postgres user:
- **On Windows:**  
```bash
psql -h localhost -U postgres -d postgres
```
- **On Linux:**  
```bash 
sudo -u postgres psql
```
#### 2.4 Execute the `ddbb.sql` script. This script will:
   - Create the `racetrack` database.
   - Create all the necessary tables.
   - Install the required extensions (`uuid-ossp`, `pgcrypto`).
   - Insert a default admin user. (READ the SCRIPT NOTE below)

Inside the `psql` console, run the following command:
```bash
\i ddbb.sql
```
✅ You should see output like:
```bash
CREATE EXTENSION
CREATE EXTENSION
NOTICE:  database "racetrack" does not exist, skipping
CREATE DATABASE
CREATE TABLE
...
INSERT 0 1
```
### 3️⃣ Script Notes

- The script includes `DROP DATABASE IF EXISTS racetrack`, so **it will delete any existing database with the same name**.
- It is intended for local or development setup.
- The default admin user is created with the username and password defined in the script. You can manually edit these values before running the script if needed.

### 4️⃣ Post-Setup Verification
- Ensure the `racetrack` database is created successfully.
- Verify that the `racetrack` database contains the necessary tables and the default admin user.

List the databases to confirm:
```bash
\l
```
List the tables in the `racetrack` database to confirm:
```bash
\dt
```
Expected output:
```bash
                List of relations
 Schema |         Name         | Type  |  Owner   
--------+----------------------+-------+----------
 public | carrera              | table | postgres
 public | carreras_programadas | table | postgres
 public | equipo               | table | postgres
 public | fulldatoscarreras    | table | postgres
 public | paradaenboxes        | table | postgres
 public | participacioncarrera | table | postgres
 public | participacionequipo  | table | postgres
 public | piloto               | table | postgres
 public | usuarios_admin       | table | postgres
 public | vuelta               | table | postgres
(10 rows)
```

### 5️⃣ Next Step
Personalize your db credentials and set up environment variables
#### 🛠️ Personalize Your Database Credentials
To connect your RaceTrack application to the PostgreSQL database, you need to set up environment variables that contain your database credentials. This is crucial for security and flexibility, allowing you to change configurations without modifying the code directly.

Create the password for the `postgres` user during PostgreSQL installation. This password will be used to connect to the database.
```bash
ALTER USER postgres WITH PASSWORD 'YOUR_PASSWORD_HERE';
```
Make sure to replace `YOUR_PASSWORD_HERE` with a strong password of your choice.

#### 🗄️ Environment Variables Setup
##### 5.1 Create a `.env` file
In the root directory of your RaceTrack project, create a file named `.env` and add the following content:

```plaintext    
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD_HERE
DB_HOST=localhost
DB_NAME=racetrack
DB_PORT=5432

# Python interpreter path for the simulation module:
# (Adjust this according to your system and environment)
PYTHON_PATH=/home/your_username/RaceTrack/venv/bin/python  # On Linux/Mac
# or on Windows:
PYTHON_PATH=C:/Path/To/venv/Scripts/python.exe
```
Replace `YOUR_PASSWORD_HERE` with the password you set for the `postgres` user during PostgreSQL installation.
Also, make sure to set PYTHON_PATH to point to the Python executable inside your virtual environment.
##### 5.2 Save the `.env` file


### 6️⃣ Uploading the data
Next step is to upload the data to the database. You can do this by running the following command in the terminal:
```bash 
python database/db_load_data.py
```
This script reads the data from the Excel files included in this repository and uploads it to the database.

The original data was extracted using the [FastF1 Python library](https://docs.fastf1.dev/) and its associated repository: [https://github.com/theOehrly/Fast-F1](https://github.com/theOehrly/Fast-F1).

The scripts used to generate these Excel files are located in the `/database/f1_library` folder.

> **Note:** These scripts are included for reference only; they are not required to run the application and can be safely removed if not needed.

## 🚀 Running the project
```bash
npm start
```

By default, the server runs on:
http://localhost:6101


## Technology Stack

- Node.js + Express + Socket.IO
- PostgreSQL (Relational database)
- Python (Prophet, Scikit-learn, XGBoost for ML)
- HTML/CSS/JavaScript (Frontend)
- WebSockets (Real-time communication)

## Author

Orianna Milone
Bachelor's Degree in Computer Engineering — CEU San Pablo University