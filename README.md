# Atomic Hostel Management System

## Project Overview

The **Atomic Hostel Management System** is a web-based application designed to simplify and automate hostel operations. It replaces traditional manual processes with a digital system that improves efficiency, accuracy, and accessibility of hostel data.

The system allows administrators to manage residents, rooms, and payments, while residents can securely access their personal information and payment history.

---

## Objectives

* Automate hostel management processes
* Improve record accuracy and reduce paperwork
* Simplify room allocation and occupancy tracking
* Manage rent payments and balances efficiently
* Provide secure access for both admin and residents

---

##  Features

###  Authentication & Security

* Admin login system
* Resident login system
* Password hashing using Werkzeug
* Password reset functionality

###  Resident Management

* Add and delete residents
* Assign residents to rooms
* Search residents by name, phone, or email

###  Room Management

* Add new rooms
* Track room capacity and occupancy
* View room availability status

###  Payment Management

* Record rent payments
* Automatically calculate balances
* View payment history

###  Reports & Dashboard

* Total residents
* Available rooms
* Total payments collected
* System summary dashboard

###  Resident Dashboard

* View personal details
* Check assigned room
* View payment history

---

##  System Architecture

The system is built using:

* **Backend:** Python (Flask)
* **Frontend:** HTML, Bootstrap
* **Database:** MySQL

---

##  Database Design

The system uses a relational database with the following structure:

* **Rooms → Residents** (One-to-Many)
* **Residents → Payments** (One-to-Many)

### Tables:

* `rooms`
* `residents`
* `payments`
* `admin`

---

##  Project Structure

```
atomic_hostel/
│
├── app.py
├── requirements.txt
├── Procfile
├── README.md
│
├── database/
│   └── schema.sql
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── residents.html
│   ├── rooms.html
│   ├── payments.html
│   ├── reports.html
│   ├── resident_login.html
│   ├── resident_dashboard.html
│   ├── reset_password.html
│
├── static/
│   ├── css/
│   ├── js/

```

---

##  Installation & Setup

### 1. Clone the repository

```
git clone [<your-repo-link>](https://github.com/DevOwen254/atomic_hostels.git)
cd atomic_hostel
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Setup database

* Create a MySQL database
* Import `database/schema.sql`

### 4. Configure environment variables

Create a `.env` file (for local use):

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=hostel_db
```

### 5. Run the application

```
python app.py
```

---

##  Deployment

The system can be deployed using:

* **Render** (backend hosting)
* **Railway** (MySQL database hosting)

---

##  Security Features

* Passwords are hashed using Werkzeug
* Protected routes using session authentication
* Role-based access (Admin vs Resident)

---

## Expected Outcomes

* Improved hostel management efficiency
* Reduced administrative workload
* Faster access to records
* Better data security and organization

---

##  Screenshots

*(Add system screenshots here for better presentation)*

---

## Author

**Owen Munene**
Student ID: 24/06934

---

## License

This project is for academic purposes.
