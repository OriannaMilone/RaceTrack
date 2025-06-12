# RaceTrack

```
npm install express nodemon socket.io
```





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
chmod +r bbdd.sql
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
#### 2.4 Execute the `bbdd.sql` script. This script will:
   - Create the `racetrack` database.
   - Create all the necessary tables.
   - Install the required extensions (`uuid-ossp`, `pgcrypto`).
   - Insert a default admin user. (READ the SCRIPT NOTE below)

Inside the `psql` console, run the following command:
```bash
\i bbdd.sql
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
