# 🚨 Emergency E-Card

### The fastest help is often the person standing closest to you.

**Emergency E-Card** is a location-aware emergency assistance platform that combines a digital emergency medical profile with real-time SOS alerts and nearby responder coordination.

**🚀 Live Demo:** [Click Here To View Our Deployed Website](https://emergency-e-card-1.onrender.com)

**📦 Repository:** [Click Here To View Our GitHub Repository](https://github.com/MakersNeedMore-MnM/Round2-BIT-CRAFT)

**🎬📊 Presentation & Demo:** [Click Here To View Our Project Presentation and Demo](https://drive.google.com/drive/folders/1qgwt4eNxSx_7NioGoX1IdSpbscnFxWXo?usp=sharing)


**Morrow 1.0 · Round 2 · Team BIT-CRAFT**

---

## ⚡ THE IDEA

During an emergency, critical information such as **blood group, allergies, medical conditions, medications, emergency contacts, and current location** should be available quickly.

Emergency E-Card brings these details together in one digital profile and connects the person in distress with nearby responders through a location-aware SOS system.

### The complete emergency flow

**Emergency occurs → SOS is triggered → Current location is captured → Nearby responders within 1 km are identified → Responder acknowledges → Navigation opens → Help is on the way → SOS is resolved**

The system supports both:

* **Self-triggered SOS** — the affected person triggers the alert directly.
* **Bystander-triggered SOS** — if the affected person is unconscious or unable to operate the application, a nearby person can use the person's phone to trigger the SOS.

> **Our goal is simple: shrink the gap between "I need help" and "someone is on the way."**

---

## 🎯 THE PROBLEM

During an emergency, the people nearby may be willing to help, but they may not have access to the information they need.

Important medical and emergency information can be:

* scattered across different places
* difficult to communicate under stress
* unavailable when the injured person cannot speak
* missing from the hands of nearby responders
* disconnected from the person's real-time location

This creates several critical gaps:

* **Medical Information Gap** — Blood group, allergies, medical conditions, medications, and emergency contacts may not be immediately available.
* **Location Gap** — Nearby people may not know exactly where assistance is needed.
* **Awareness Gap** — People capable of helping may not know that someone nearby needs assistance.
* **Response Gap** — The person requesting help may not know whether someone has actually accepted the emergency.
* **Coordination Gap** — Even after someone responds, reaching the emergency location can require additional communication.

---

## 💡 THE SOLUTION

Emergency E-Card combines three essential capabilities:

|                      |                                    |
| -------------------- | ---------------------------------- |
| 🪪 **Who You Are**   | Digital Emergency Medical Profile  |
| 📍 **Where You Are** | Live Location + Location-Aware SOS |
| 🤝 **Who Is Coming** | Nearby Responder Coordination      |

The user creates an Emergency E-Card once and stores important emergency information such as:

* Full name
* Phone number
* Blood group
* Allergies
* Medical conditions
* Current medications
* Emergency contacts

The application also tracks the user's current browser/device location while the app is active.

When an SOS is triggered, the current coordinates are associated with the emergency alert. Nearby users within the supported **1 km radius** can discover the alert, acknowledge that they are coming to help, and navigate to the emergency location.

---

## ✨ KEY FEATURES

### 🪪 Emergency Medical Profile

Users create a digital emergency profile containing:

* Full name
* Phone number
* Blood group
* Allergies
* Medical conditions
* Current medications
* Emergency contacts
* Current location

The information is stored centrally so it can be retrieved during an emergency without requiring the user to manually provide every detail.

---

### 🚑 Emergency Details Access

The application provides an emergency details view containing important medical information from the profile.

Responders can access relevant emergency information such as:

* Patient name
* Phone number
* Blood group
* Allergies
* Medical conditions
* Medications
* Emergency contacts

This is designed to reduce the time spent collecting critical information during an emergency.

---

### 📍 Live Location Tracking

The application continuously monitors the user's browser/device location while the application is active.

The latest coordinates are synchronized with the user's emergency profile so that the system can work with the user's current location.

When an SOS is triggered, the current coordinates are used for the emergency alert and nearby responder calculations.

---

### 🆘 One-Tap SOS

A user can trigger an emergency alert using the SOS flow.

The SOS includes:

* Emergency profile information
* Current latitude and longitude
* A unique emergency alert ID
* Nearby responder discovery

The alert remains active until it is resolved by the SOS owner or reaches its expiry conditions.

---

### 📍 1 km Nearby Emergency Detection

SOS alerts are location-aware.

The current prototype uses a **1 km proximity boundary** for nearby emergency discovery and responder acknowledgement.

This means:

* Users within the supported radius can discover relevant emergencies.
* Users outside the supported radius do not see unrelated nearby SOS alerts.
* Responder acknowledgement is validated using location.

This prevents an emergency alert from being unnecessarily exposed to distant users.

---

### 🤝 "I'm on the Way"

A nearby responder can acknowledge an active emergency using the **"I'm on the Way"** action.

The backend validates the responder and stores the acknowledgement.

The SOS owner can then see that a responder has accepted the emergency.

---

### ⚡ Real-Time Responder Updates

The SOS owner receives responder information through a **WebSocket connection** without manually refreshing the application.

The response information can include:

* Responder name
* Responder phone number
* Response status
* Number of responders

This allows the person requesting help to know when someone is actively responding.

---

### 👥 Multiple Responder Support

More than one nearby responder can acknowledge the same emergency.

Each acknowledgement is stored independently, allowing the SOS owner to see multiple people responding to the same alert.

---

### 🗺️ Google Maps Navigation

Once a responder acknowledges the emergency, the responder dashboard provides a **"Navigate to SOS"** action.

The system opens Google Maps with the emergency coordinates as the destination, allowing the responder to navigate directly to the SOS location.

---

### 🛡️ Owner-Controlled SOS Resolution

Only the profile that created the SOS can resolve the active emergency.

The owner can use:

**"End SOS (I'm Safe)"**

Once the emergency is ended:

* The active alert is resolved.
* The alert is removed from active responder views.
* Responders no longer see it as an active emergency.

---

### 👤 Self-Triggered Emergency

When the person in distress is conscious and able to use their phone:

**Open E-Card → Trigger SOS → Location is captured → Nearby responders receive the alert → Responder acknowledges → Navigation begins**

---

### 👥 Bystander-Triggered Emergency

When the injured person is unconscious or unable to operate the application:

**Bystander uses the person's phone → Triggers SOS → Current location is captured → Nearby responders receive the alert → Responder acknowledges → Navigation begins**

This provides a way to request additional nearby help even when the affected person cannot interact with the application themselves.

---

## 🔄 HOW IT WORKS

```text
             CREATE EMERGENCY E-CARD
                       │
                       ▼
              LIVE LOCATION ACTIVE
                       │
                       ▼
                  TRIGGER SOS
                       │
                       ▼
          CAPTURE CURRENT GPS LOCATION
                       │
                       ▼
          FIND RESPONDERS WITHIN 1 KM
                       │
                       ▼
             RESPONDER SEES ALERT
                       │
                       ▼
              "I'M ON THE WAY"
                       │
                       ▼
             SERVER-SIDE VALIDATION
                       │
                       ▼
              STORE ACKNOWLEDGEMENT
                       │
                       ▼
          REAL-TIME WEBSOCKET UPDATE
                       │
                       ▼
        SOS OWNER SEES THE RESPONDER
                       │
                       ▼
              NAVIGATE TO SOS
                       │
                       ▼
                 HELP ARRIVES
                       │
                       ▼
              "END SOS (I'M SAFE)"
```

### Emergency Flow

1. **Create Profile** — Enter medical and emergency information.
2. **Enable Location** — Allow browser/device location access.
3. **Track Location** — The application keeps the profile's location updated while active.
4. **Trigger SOS** — Create an active emergency alert using the current coordinates.
5. **Find Nearby Responders** — The backend identifies relevant users within the supported 1 km radius.
6. **Display Alert** — Nearby responders see the emergency on their dashboard.
7. **Acknowledge** — A responder selects **"I'm on the Way."**
8. **Validate** — The backend verifies the alert, responder, location, proximity, expiry, and duplicate conditions.
9. **Store** — The acknowledgement is stored in PostgreSQL.
10. **Notify** — A WebSocket event updates the SOS owner's active session.
11. **Navigate** — The responder can open Google Maps using the SOS coordinates.
12. **Resolve** — The SOS owner ends the emergency once safe.

---

## 🧠 TECHNICAL HIGHLIGHTS

### ⚡ Real-Time Communication

The application uses **WebSockets** to push responder information to the SOS owner's active session.

There is no need for continuous polling or manual page refreshes to receive responder updates.

---

### 📍 Live Location Synchronization

The frontend uses the browser's Geolocation API to monitor the user's current position.

Location updates are sent to the backend and associated with the user's emergency profile.

When an SOS is triggered, the latest available coordinates are passed to the backend so the emergency uses the current location rather than relying only on older profile data.

---

### 📍 Location-Based Alert Filtering

The backend performs proximity calculations to identify nearby users.

The prototype uses a **1 km radius** for responder discovery and acknowledgement.

The backend also validates latitude and longitude ranges before using coordinates in emergency operations.

---

### 🔐 Server-Side Validation

Emergency actions are enforced by the backend rather than relying only on frontend restrictions.

The backend validates:

* Alert status
* Alert expiry
* Profile identity
* Responder identity
* GPS coordinates
* Proximity to the emergency
* Duplicate acknowledgements
* SOS ownership during resolution

---

### 👥 Multiple Responder Support

Multiple responders can acknowledge the same emergency.

Each responder is stored independently and can be delivered to the SOS owner in real time.

---

### 🛡️ Duplicate Protection

The backend prevents the same responder from acknowledging the same emergency multiple times.

Database constraints provide an additional protection layer against duplicate acknowledgement records.

---

## 🏗️ ARCHITECTURE

Emergency E-Card is a full-stack system built around REST APIs, browser geolocation, location-based alert discovery, PostgreSQL persistence, and WebSockets.

```text
┌─────────────────────────────────────┐
│            React Frontend           │
│         TypeScript + Vite           │
│                                     │
│  UI · Geolocation · REST · WebSocket│
└──────────────────┬──────────────────┘
                   │
             REST API + WebSocket
                   │
                   ▼
┌─────────────────────────────────────┐
│            FastAPI Backend           │
│                                     │
│ Profiles · SOS · Location           │
│ Proximity · Responders              │
│ Validation · Resolution             │
│ Real-Time Notifications             │
└──────────────────┬──────────────────┘
                   │
                SQLAlchemy
                   │
                   ▼
┌─────────────────────────────────────┐
│         PostgreSQL Database         │
│          Neon Production            │
└─────────────────────────────────────┘
```

### Frontend

React and TypeScript provide the application interface.

The frontend uses:

* Axios for REST API communication
* Browser Geolocation API for live location
* WebSockets for real-time responder updates
* React Router for navigation

### Backend

FastAPI handles:

* Profile creation and updates
* Live profile location updates
* Emergency alerts
* Proximity calculations
* Responder acknowledgement
* Server-side validation
* SOS resolution
* WebSocket notifications

### Database

PostgreSQL stores:

* Emergency profiles
* Emergency alerts
* Responder acknowledgements

**Neon PostgreSQL** is used for the production database.

---

## 🛠️ TECHNOLOGY STACK

| Layer                       | Technologies                          |
| --------------------------- | ------------------------------------- |
| **Frontend**                | React, TypeScript, Vite, Tailwind CSS |
| **Location**                | Browser Geolocation API               |
| **API Communication**       | REST, Axios                           |
| **Real-Time Communication** | WebSockets                            |
| **Backend**                 | Python, FastAPI, Uvicorn              |
| **ORM**                     | SQLAlchemy                            |
| **Database**                | PostgreSQL, Neon                      |
| **Navigation**              | Google Maps                           |
| **Deployment**              | Render                                |
| **Version Control**         | Git, GitHub                           |

---

## 🚀 LIVE APPLICATION

**Try Emergency E-Card:**

https://emergency-e-card-1.onrender.com

### For Someone Requesting Help

1. Create your Emergency E-Card.
2. Enter your medical and emergency information.
3. Allow location access.
4. Keep the application active so the current location can be synchronized.
5. Trigger an SOS during an emergency.
6. Nearby responders can discover the alert within the supported 1 km radius.
7. See responder acknowledgements in real time.
8. End the SOS using **"End SOS (I'm Safe)"** once safe.

### For Someone Helping

1. Open the application.
2. View active emergencies near you.
3. Open a relevant emergency alert.
4. Review the available emergency information.
5. Select **"I'm on the Way."**
6. Use **"Navigate to SOS"** to open Google Maps.
7. Travel to the emergency location.

> **Prototype note:** The backend runs on Render's free tier. After inactivity, the first request may take some time while the service wakes up.

---

## 📊 DEPLOYMENT VERIFICATION

The deployed application has been practically tested through the complete emergency workflow.

### Verified production behaviours

* Emergency profile access
* Live browser location retrieval
* Location-aware SOS triggering
* Nearby SOS alert detection
* **1 km proximity filtering**
* Responder acknowledgement using **"I'm on the Way"**
* Real-time responder updates
* Responder details
* Google Maps navigation to SOS coordinates
* SOS resolution / **"End SOS"**
* Alert removal after resolution
* Location-based isolation between distant users
* PostgreSQL persistence through Neon
* Frontend-to-backend communication through the deployed system

### Practical location test

The location filtering was tested using real users in different physical locations.

A nearby responder could receive the relevant SOS, while a user located far outside the supported radius could not see that emergency.

The reverse case was also verified, confirming that distant users do not receive unrelated SOS alerts.

---

## 📂 PROJECT STRUCTURE

```text
Round2-BIT-CRAFT/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── test_main.py
│   └── README.md
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── .gitignore
└── README.md
```

---

## ☁️ PRODUCTION DEPLOYMENT

The production architecture uses:

```text
Render Static Site
        │
        ▼
React Frontend
        │
        │ REST API + WebSocket
        ▼
Render Web Service
        │
        ▼
FastAPI Backend
        │
        ▼
Neon PostgreSQL
```

The deployed application is available at:

**https://emergency-e-card-1.onrender.com**

---

## 🔮 FUTURE SCOPE

The prototype can be extended with:

* Interactive emergency maps and richer live navigation
* Push notifications for nearby emergencies
* Automatic emergency-contact notifications
* Ambulance and hospital integration
* Verified responder accounts
* Native mobile applications
* Offline emergency support
* Background location support
* Emergency incident analytics
* Integration with official emergency-service workflows

---

## ⚠️ PROTOTYPE DISCLAIMER

**Emergency E-Card is a hackathon prototype.**

It does **not** contact official emergency services such as police, ambulance, or fire services and is **not a replacement for official emergency services**.

Users should not rely on this prototype as their sole means of obtaining emergency assistance.

---

## 👥 TEAM BIT-CRAFT

| Member             | Role                            |
| ------------------ | ------------------------------- |
| **Mohammad Hasan** | Team Leader & Backend Developer |
| **Niranjan S J**   | Team Member                     |
| **Jaiabner N**     | Team Member                     |

**Hackathon:** Morrow 1.0 by Makers Need More
**Round:** Round 2 — Project & Prototype Submission

> 🚨 **Because sometimes the nearest help is just around the corner.**

**Built with ❤️ by Team BIT-CRAFT**
