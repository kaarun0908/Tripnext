# TripNest — Smart Tourist Booking System

**TripNest** is a modern, responsive, full-stack tourist booking web application built with **Python 3**, **Flask**, **SQLite**, **Flask-SQLAlchemy**, **Flask-Migrate**, **Flask-Login**, **Flask-WTF**, and **Bootstrap 5**.

The platform is inspired by world-class travel platforms, allowing tourists to discover curated Indian destinations (Ooty, Kodaikanal, Munnar, Goa, Jaipur, Manali, Mysuru, Alleppey), reserve packages, book hotel rooms with guaranteed inventory locking (eliminating overbooking), execute simulated transactions, and post verified feedback. Administrators have full visibility into live analytics, revenue charts, inventory CRUD, and CSV report export.

---

## 🌟 Key Features

### Customer Experience
- **Interactive Destination Explorer**: Filter by category (Hill Station, Beach, Heritage, Backwaters), budget, or search query with live sorting.
- **Curated Tour Packages**: Handcrafted multi-day packages with day-by-day itineraries and transparent pricing.
- **Hotels & Room Inventory**: Detailed amenities, capacity enforcement, and date-range calculations.
- **Concurrency-Safe Booking**: Guaranteed room inventory allocation using database transactions and row-level locking.
- **Simulated Payment Sandbox**: Safe payment simulation (UPI Demo, Card Demo, Pay at Property / COD) with instant status changes and audit tracking.
- **Tourist Dashboard & Favourites**: Track upcoming trips, pending payments, booking history, and wishlisted destinations.
- **Verified Customer Reviews**: Only tourists with verified reservations can submit reviews.

### Administrator Operations
- **Interactive Analytics Dashboard**: Live metrics, revenue trends, booking distributions, and destination popularity powered by Chart.js.
- **Entity Management (CRUD)**: Create, read, update, and deactivate destinations, packages, hotels, and rooms.
- **Booking Fulfillment**: Update statuses (`PENDING`, `CONFIRMED`, `COMPLETED`, `CANCELLED`) with automatic inventory management.
- **Audit Logging**: Every status transition is timestamped and recorded in `booking_status_history`.
- **CSV Data Export**: Instant download of customer bookings for accounting and business reporting.

---

## 🛠 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3, Flask, Werkzeug, python-dotenv |
| **Database** | SQLite 3 (ACID compliant, zero configuration) &amp; PostgreSQL ready |
| **Security & Auth**| Flask-Login, Werkzeug Password Hashing, Flask-WTF (CSRF) |
| **Frontend** | Jinja2 Templates, Bootstrap 5.3, Bootstrap Icons, Custom CSS |
| **Charts** | Chart.js |
| **Production WSGI**| Gunicorn |
| **Testing** | Pytest (20 automated unit & integration tests) |

---

## 📁 Project Structure

```
TripNest/
├── app/
│   ├── __init__.py                 # Application factory & Jinja filters
│   ├── extensions.py               # db, migrate, login_manager, csrf
│   ├── models.py                   # 13 normalized PostgreSQL models
│   ├── forms.py                    # WTForms with validation rules
│   ├── decorators.py               # Role-based access control (@admin_required)
│   ├── services/
│   │   ├── booking_service.py      # Inventory lock, date math, cancellation
│   │   ├── payment_service.py      # Simulation logic & status changes
│   │   └── report_service.py       # SQL aggregates, Chart.js feeds, CSV export
│   ├── auth/                       # Blueprint for login, register, logout
│   ├── main/                       # Blueprint for home, destinations, hotels
│   ├── bookings/                   # Blueprint for reservation & payment workflow
│   ├── admin/                      # Blueprint for operations & moderation
│   ├── templates/                  # Base & customer views
│   │   ├── admin/                  # Administrative views & management forms
│   │   └── errors/                 # 403, 404, 500 error templates
│   └── static/
│       ├── css/style.css           # Modern Ocean Teal & Coral palette
│       └── js/                     # AJAX favourite toggle, dynamic calculator
├── scripts/
│   ├── seed_data.py                # Comprehensive Indian tourism dataset
│   └── reporting_queries.sql       # SQL views, joins, aggregates & audit demo
├── tests/                          # 20 automated pytest test cases
├── config.py                       # Environment-aware configuration
├── run.py                          # Development entrypoint
├── requirements.txt                # Exact pinned dependencies
├── .env.example                    # Environment variable template
└── README.md
```

---

## 🚀 Local Installation & Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- PostgreSQL 14+ installed and running
- Git

### 2. Database Setup (PostgreSQL)
Open your PostgreSQL terminal (`psql` or pgAdmin) and create the development and testing databases:

```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE tripnest OWNER postgres;
CREATE DATABASE tripnest_test OWNER postgres;
```

### 3. Virtual Environment & Dependencies
Clone the repository and set up a virtual environment:

```bash
cd TripNest

# Create and activate virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Verify your database connection parameters in `.env`:
```ini
SECRET_KEY=your-super-secret-key-here
FLASK_APP=run.py
FLASK_ENV=development
DEBUG=True

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tripnest
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tripnest_test
PORT=5000
```

### 5. Initialize Database & Run Migrations
Run the Flask seed script to create all schema tables, constraints, and rich Indian tourism demo data:

```bash
python scripts/seed_data.py
```

Or using the Flask CLI:
```bash
flask seed-db
```

### 6. Run the Application Locally
```bash
python run.py
```
Open your browser and visit: **http://localhost:5000**

---

## 🔑 Demo Accounts

The seed script creates the following pre-configured demonstration accounts:

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@tripnest.com` | `Admin@12345` | Full Admin Portal, CRUD, Analytics, CSV Export |
| **Tourist Customer** | `priya.sharma@example.com` | `Customer@123` | Booking, Payments, Reviews, Wishlist |
| **Tourist Customer 2**| `rahul.verma@example.com` | `Customer@123` | Booking, Profile Management |

*Note: Quick-fill buttons are integrated directly into the Sign In page for one-click demo login.*

---

## 🧪 Running Automated Tests

Run the complete test suite with pytest:

```bash
python -m pytest tests/ -v
```

The 20 automated tests verify:
- ✅ Customer registration with password hashing and duplicate prevention
- ✅ Login authentication, remember-me sessions, and invalid credential handling
- ✅ Destination search, category filtering, and sorting
- ✅ Package pricing algorithms across traveller counts
- ✅ Hotel room capacity enforcement and date validation
- ✅ Room availability checking and **concurrency overbooking prevention**
- ✅ Reservation cancellation and automatic inventory release
- ✅ Payment simulations (success vs failed transaction states)
- ✅ Prevention of duplicate payments on confirmed bookings
- ✅ Role-based authorization (`@admin_required` with 403 enforcement)
- ✅ Administrative CRUD and CSV export functionality

---

## 📊 SQL and DBMS Demonstration

TripNest includes real-world relational database patterns documented in `scripts/reporting_queries.sql`:
1. **Views**: `view_booking_summaries`, `view_destination_popularity`, `view_monthly_revenue_report`.
2. **Aggregations**: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` with `GROUP BY` and `HAVING`.
3. **Concurrency Control**: `SELECT ... FOR UPDATE` row locks to prevent room overbooking.
4. **Audit History**: `booking_status_history` logging user ID, old status, new status, and remarks.

Execute in PostgreSQL:
```bash
psql -U postgres -d tripnest -f scripts/reporting_queries.sql
```

---

## ☁️ Deployment Guide (Render / Cloud)

### 1. Render Deployment Steps
1. Create a new **PostgreSQL Database** on Render.
2. Create a new **Web Service** connected to your GitHub repository.
3. Set the environment:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
4. Add the following **Environment Variables**:
   - `DATABASE_URL`: *(Your Render PostgreSQL Internal Connection String)*
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `FLASK_ENV`: `production`
5. After the initial build finishes, open the Render Shell and seed data:
   ```bash
   python scripts/seed_data.py
   ```

---

## 📄 License
This project is open-source under the MIT License.
