from getpass import getpass

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal, configure_database, new_uuid, utcnow
from app.models import AuditLog, AuthSession, Role, User
from app.security import hash_password

SUPERADMIN_EMAIL = "superadmin@gym.local"


def main() -> None:
    settings = get_settings()
    engine = configure_database(settings.database_url)
    if engine.dialect.name == "sqlite":
        raise SystemExit(
            "Refusing to reset a local SQLite database. Run this command in the API service "
            "with its Railway database configured."
        )

    password = getpass("New API superadmin password (min 10 characters): ")
    confirmation = getpass("Confirm new API superadmin password: ")
    if len(password) < 10 or len(password) > 256:
        raise SystemExit("Password must be between 10 and 256 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.email == SUPERADMIN_EMAIL))
        if user is None or user.role != Role.SUPER_ADMIN:
            raise SystemExit(f"Superadmin account {SUPERADMIN_EMAIL} was not found.")

        user.password_hash = hash_password(password)
        for session in db.scalars(
            select(AuthSession).where(
                AuthSession.user_id == user.id,
                AuthSession.revoked_at.is_(None),
            )
        ):
            session.revoked_at = utcnow()

        db.add(
            AuditLog(
                actor_type="SYSTEM",
                actor_id=None,
                action="AUTH_PASSWORD_RESET",
                resource_type="user",
                resource_id=user.id,
                before_data=None,
                after_data={"email": user.email},
                ip_address=None,
                user_agent=None,
                correlation_id=new_uuid(),
            )
        )

    print(f"Password reset for {SUPERADMIN_EMAIL}.")


if __name__ == "__main__":
    main()
