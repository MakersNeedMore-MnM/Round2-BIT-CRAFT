import uuid
import math
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, String, Text, DateTime, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# --- Database Setup ---
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./emergency_ecard.db"
)

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- SQLAlchemy Models ---
def generate_uuid():
    return str(uuid.uuid4())

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    full_name = Column(String, index=True)
    phone_number = Column(String)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    blood_group = Column(String)
    allergies = Column(Text)
    medical_conditions = Column(Text)
    medications = Column(Text)
    # Storing emergency contacts as a simple string or JSON string for MVP
    emergency_contacts = Column(Text)
class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    profile_id = Column(String, nullable=False)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
# Create the tables
Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class ProfileBase(BaseModel):
    full_name: str
    phone_number: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    emergency_contacts: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    emergency_contacts: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, profile_id: str):
        await websocket.accept()
        self.active_connections[profile_id] = websocket

    def disconnect(self, profile_id: str):
        if profile_id in self.active_connections:
            del self.active_connections[profile_id]

    async def send_personal_message(self, message: dict, profile_id: str):
        if profile_id in self.active_connections:
            try:
                await self.active_connections[profile_id].send_json(message)
            except Exception:
                self.disconnect(profile_id)

manager = ConnectionManager()


# --- FastAPI App ---
app = FastAPI(title="Emergency E-Card API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def migrate_database():
    inspector = inspect(engine)
    if "emergency_alerts" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("emergency_alerts")]
        db = SessionLocal()
        try:
            if "created_at" not in columns:
                db.execute(text("ALTER TABLE emergency_alerts ADD COLUMN created_at DATETIME"))
            if "expires_at" not in columns:
                db.execute(text("ALTER TABLE emergency_alerts ADD COLUMN expires_at DATETIME"))
            
            db.commit()
            
            # Backfill existing active records to prevent NULL expires_at bugs
            current_time = datetime.now(timezone.utc)
            db.execute(
                text("""
                UPDATE emergency_alerts 
                SET 
                    created_at = :current_time,
                    expires_at = :future_time 
                WHERE status = 'active' AND (created_at IS NULL OR expires_at IS NULL)
                """),
                {"current_time": current_time, "future_time": current_time + timedelta(minutes=10)}
            )
            
            # For historically resolved alerts, we don't care about expires_at being NULL
            # but setting created_at to current_time is better than NULL for schema consistency
            db.execute(
                text("""
                UPDATE emergency_alerts 
                SET created_at = :current_time
                WHERE status != 'active' AND created_at IS NULL
                """),
                {"current_time": current_time}
            )
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to migrate emergency_alerts schema: {e}")
            raise e
        finally:
            db.close()
            
    if "profiles" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("profiles")]
        db = SessionLocal()
        try:
            if "latitude" not in columns:
                db.execute(text("ALTER TABLE profiles ADD COLUMN latitude VARCHAR"))
            if "longitude" not in columns:
                db.execute(text("ALTER TABLE profiles ADD COLUMN longitude VARCHAR"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to migrate profiles schema: {e}")
            raise e
        finally:
            db.close()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two GPS coordinates in kilometers.
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
# --- Endpoints ---

@app.websocket("/ws/alerts/{profile_id}")
async def websocket_endpoint(websocket: WebSocket, profile_id: str):
    await manager.connect(websocket, profile_id)
    try:
        while True:
            # Keep connection alive, though client only receives
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(profile_id)


@app.post("/profiles/", response_model=ProfileResponse, status_code=201)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """
    Create a new emergency profile.
    """
    db_profile = Profile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    Retrieve an emergency profile using a unique profile ID.
    """
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

@app.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: str, profile: ProfileUpdate, db: Session = Depends(get_db)):
    """
    Update an existing profile.
    """
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/sos/{profile_id}")
async def sos_alert(profile_id: str, db: Session = Depends(get_db)):
    """
    Trigger an SOS alert, save the emergency event,
    and find nearby registered users.
    """

    db_profile = db.query(Profile).filter(
        Profile.id == profile_id
    ).first()

    if db_profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    if db_profile.latitude is None or db_profile.longitude is None:
        raise HTTPException(
            status_code=400,
            detail="Profile location is not available"
        )

    current_time = datetime.now(timezone.utc)
    
    # Check for existing active, unexpired alert
    existing_alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.profile_id == profile_id,
        EmergencyAlert.status == "active",
        EmergencyAlert.expires_at > current_time
    ).first()

    if existing_alert:
        return {
            "message": "SOS Alert already active",
            "alert_id": existing_alert.id,
            "profile_id": db_profile.id,
            "full_name": db_profile.full_name,
            "latitude": existing_alert.latitude,
            "longitude": existing_alert.longitude,
            "blood_group": db_profile.blood_group,
            "allergies": db_profile.allergies,
            "medical_conditions": db_profile.medical_conditions,
            "emergency_contacts": db_profile.emergency_contacts,
            "nearby_users": []  # Existing logic wouldn't re-notify
        }

    # Create and save new emergency alert
    expires_at = current_time + timedelta(minutes=10)
    emergency_alert = EmergencyAlert(
        profile_id=db_profile.id,
        latitude=db_profile.latitude,
        longitude=db_profile.longitude,
        status="active",
        created_at=current_time,
        expires_at=expires_at
    )

    db.add(emergency_alert)
    db.commit()
    db.refresh(emergency_alert)

    # Find nearby users
    all_profiles = db.query(Profile).filter(
        Profile.id != profile_id
    ).all()

    nearby_users = []

    for profile in all_profiles:
        if profile.latitude is None or profile.longitude is None:
            continue

        distance = calculate_distance(
            db_profile.latitude,
            db_profile.longitude,
            profile.latitude,
            profile.longitude
        )

        if distance <= 1.0:
            nearby_users.append({
                "profile_id": profile.id,
                "full_name": profile.full_name,
                "distance_km": round(distance, 2)
            })
            
            # Broadcast via WebSocket if the nearby user is connected
            ws_payload = {
                "type": "ALERT_CREATED",
                "data": {
                    "alert_id": emergency_alert.id,
                    "profile_id": db_profile.id,
                    "full_name": db_profile.full_name,
                    "latitude": db_profile.latitude,
                    "longitude": db_profile.longitude,
                    "distance_km": round(distance, 2),
                    "expires_at": expires_at.isoformat()
                }
            }
            await manager.send_personal_message(ws_payload, profile.id)

    return {
        "message": "SOS Alert Triggered",
        "alert_id": emergency_alert.id,
        "profile_id": db_profile.id,
        "full_name": db_profile.full_name,
        "latitude": db_profile.latitude,
        "longitude": db_profile.longitude,
        "blood_group": db_profile.blood_group,
        "allergies": db_profile.allergies,
        "medical_conditions": db_profile.medical_conditions,
        "emergency_contacts": db_profile.emergency_contacts,
        "nearby_users": nearby_users
    }
@app.get("/nearby/{profile_id}")
def find_nearby_users(
    profile_id: str,
    radius_km: float = 1.0,
    db: Session = Depends(get_db)
):
    """
    Find registered users within a given radius of the specified profile.
    """

    emergency_profile = db.query(Profile).filter(
        Profile.id == profile_id
    ).first()

    if emergency_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    if emergency_profile.latitude is None or emergency_profile.longitude is None:
        raise HTTPException(
            status_code=400,
            detail="Profile location is not available"
        )

    all_profiles = db.query(Profile).filter(
        Profile.id != profile_id
    ).all()

    nearby_users = []

    for profile in all_profiles:
        if profile.latitude is None or profile.longitude is None:
            continue

        distance = calculate_distance(
            emergency_profile.latitude,
            emergency_profile.longitude,
            profile.latitude,
            profile.longitude
        )

        if distance <= radius_km:
            nearby_users.append({
                "profile_id": profile.id,
                "full_name": profile.full_name,
                "distance_km": round(distance, 2)
            })

    return {
        "emergency_profile_id": profile_id,
        "radius_km": radius_km,
        "nearby_users": nearby_users
    }
@app.get("/alerts/{profile_id}")
def get_nearby_alerts(
    profile_id: str,
    radius_km: float = 1.0,
    db: Session = Depends(get_db)
):
    """
    Find active emergency alerts near a registered user.
    """

    responder = db.query(Profile).filter(
        Profile.id == profile_id
    ).first()

    if responder is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    if responder.latitude is None or responder.longitude is None:
        raise HTTPException(
            status_code=400,
            detail="Responder location is not available"
        )

    current_time = datetime.now(timezone.utc)
    active_alerts = db.query(EmergencyAlert).filter(
        EmergencyAlert.status == "active",
        EmergencyAlert.expires_at > current_time
    ).all()

    nearby_alerts = []

    for alert in active_alerts:
        if alert.latitude is None or alert.longitude is None:
            continue

        if alert.profile_id == profile_id:
            continue

        distance = calculate_distance(
            responder.latitude,
            responder.longitude,
            alert.latitude,
            alert.longitude
        )

        if distance <= radius_km:
            emergency_profile = db.query(Profile).filter(
                Profile.id == alert.profile_id
            ).first()

            nearby_alerts.append({
                "alert_id": alert.id,
                "profile_id": alert.profile_id,
                "full_name": emergency_profile.full_name if emergency_profile else None,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "distance_km": round(distance, 2),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
            })

    return {
        "responder_profile_id": profile_id,
        "radius_km": radius_km,
        "nearby_alerts": nearby_alerts
    }


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Mark an emergency alert as resolved.
    """
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == alert_id
    ).first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.status = "resolved"
    db.commit()
    db.refresh(alert)

    # Broadcast resolution to nearby connected users
    all_profiles = db.query(Profile).all()
    for profile in all_profiles:
        if profile.latitude and profile.longitude and alert.latitude and alert.longitude:
            distance = calculate_distance(
                alert.latitude, alert.longitude,
                profile.latitude, profile.longitude
            )
            if distance <= 1.0:
                ws_payload = {
                    "type": "ALERT_RESOLVED",
                    "data": {
                        "alert_id": alert.id
                    }
                }
                await manager.send_personal_message(ws_payload, profile.id)

    return {
        "message": "Alert resolved successfully",
        "alert_id": alert.id,
        "status": alert.status
    }