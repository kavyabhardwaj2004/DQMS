# 🏥 DQMS: Digital Queue Management System

> **A Full-Stack, Real-Time Queuing Solution powered by AI Logic & WebSockets.**

## 🔴 Live Demo Status:
This project is currently hosted locally. The demo link is active only while the host machine is running.
**Link** : https://3937865528df74eb-49-43-169-191.serveousercontent.com/

## 💡 About The Project
**DQMS** (Digital Queue Management System) is designed to solve the problem of chaotic physical queues in banks, hospitals, and service centers.

Unlike traditional systems, this project utilizes **Real-Time WebSockets** to update screens instantly without refreshing and incorporates **Rule-Based AI** to detect emergency cases and prioritize them automatically.

---

## 🏗️ System Architecture
The system follows a monolithic Full-Stack architecture integrating a Flask backend with a persistent SQLite database and a responsive frontend.

![Architecture Diagram](https://github.com/user-attachments/assets/PLACEHOLDER_FOR_YOUR_IMAGE_LINK)
*(Upload your flow diagram here)*

---

## 🚀 Key Features

### 1. ⚡ Real-Time Synchronization
- Uses **Flask-SocketIO** to establish a bi-directional channel between the Server, Admin, and User.
- When a user joins, the Admin's list updates **instantly**.
- When the Admin calls a number, the User's screen flashes/alerts **instantly**.

### 2. 🧠 AI & Priority Logic
- **NLP keyword extraction:** The system scans the 'Reason' for visit.
- **Emergency Handling:** If inputs contain words like *"Emergency", "Critical",* or *"Severe"*:
    - The Wait Time is set to **0 minutes**.
    - The User is moved to the **front of the queue** automatically.
- **Wait Time Regression:**
    - Standard Formula: `Time = (Queue Length * 5 minutes) + Buffer`.

### 3. 🛡️ Admin Dashboard
- Visual differentiation between **Urgent** (Red) and **Normal** (Blue) tokens.
- Single-click "Call Next" functionality.
- Live view of "Now Serving".

### 4. 💾 Data Persistence
- Uses **SQLite** with **SQLAlchemy ORM**.
- Ensures that the queue state is saved even if the server restarts.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python (Flask) |
| **Database** | SQLite (SQLAlchemy) |
| **Real-Time Engine** | Flask-SocketIO |
| **Frontend** | HTML5, CSS3 (Gradient UI), JavaScript |
| **Deployment** | Render / Ngrok Tunneling |

---

## 🔧 How to Run Locally

### Prerequisites
- Python 3.x installed
- Git installed

### Step 1: Clone the Repository
```bash
git clone https://github.com/kavyabhardwaj2004/DQMS.git
cd DQMS
