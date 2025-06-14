# RaceTrack
RaceTrack is a web application designed to... 


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
```
Replace `YOUR_PASSWORD_HERE` with the password you set for the `postgres` user during PostgreSQL installation.
##### 5.2 Save the `.env` file


### Uploading the data
Next step is to upload the data to the database. You can do this by running the following command in the terminal:
```bash 
python /database/db_load_data.py
```
