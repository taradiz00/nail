from app.core.database import SessionLocal
from app.models.service import Service


db = SessionLocal()

try:
    services = [
        Service(
            name="کاشت یا ترمیم",
            category="hand",
            deposit_amount=200000,
            price=None,
            duration_minutes=60,
            is_active=True,
        ),
        Service(
            name="کاشت یا ترمیم",
            category="foot",
            deposit_amount=200000,
            price=None,
            duration_minutes=60,
            is_active=True,
        ),
        Service(
            name="طراحی",
            category="design",
            deposit_amount=200000,
            price=None,
            duration_minutes=60,
            is_active=True,
        ),
    ]

    db.add_all(services)
    db.commit()

finally:
    db.close()