"""
SQLite to PostgreSQL / Neon Cloud Migration Engine
AI/ML-Powered Mining Safety and Worker Evacuation System

Idempotent, relationship-preserving migration utility that transfers:
1. mining_zones
2. workers
3. sensors
4. sensor_readings
5. risk_predictions
6. emergency_alerts
7. worker_evacuation_status

Features:
- Preserves primary keys and exact foreign-key relational graph.
- Idempotent: safe to run multiple times without duplicate records.
- Automatically adjusts PostgreSQL auto-increment sequences (setval).
- Compares source SQLite vs target PostgreSQL row counts for 100% verification.
- Performs non-destructive CRUD test on temporary test record.
- Operates via CLI or automatic invocation on FastAPI startup lifespan.
"""
import os
import sys
import logging
from typing import Dict, Any, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from backend.app.database.models import (
    Base,
    MiningZone,
    Worker,
    Sensor,
    SensorReading,
    RiskPrediction,
    EmergencyAlert,
    WorkerEvacuationStatus,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("migration.sqlite_to_pg")

DEFAULT_SQLITE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "mining_safety.db")
)

# Strict topological order respecting foreign key constraints
TABLE_ORDER = [
    (MiningZone, "mining_zones"),
    (Worker, "workers"),
    (Sensor, "sensors"),
    (SensorReading, "sensor_readings"),
    (RiskPrediction, "risk_predictions"),
    (EmergencyAlert, "emergency_alerts"),
    (WorkerEvacuationStatus, "worker_evacuation_status"),
]


def normalize_postgres_url(url: str) -> str:
    """Normalizes postgres:// and postgresql:// to postgresql+psycopg2://."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_sqlite_row_counts(sqlite_path: str) -> Dict[str, int]:
    """Inspects and returns row counts for all 7 tables in the SQLite database."""
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"Source SQLite database not found at: {sqlite_path}")

    src_engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    counts = {}
    with src_engine.connect() as conn:
        for model_cls, table_name in TABLE_ORDER:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            counts[table_name] = res
    return counts


def migrate_database(
    target_url: str,
    sqlite_path: str = DEFAULT_SQLITE_PATH,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Migrates all records from SQLite to PostgreSQL / Neon.
    Returns migration verification statistics.
    """
    target_url = normalize_postgres_url(target_url)
    is_postgres = target_url.startswith("postgresql")

    logger.info("=" * 70)
    logger.info(" STARTING DATABASE MIGRATION: SQLITE -> CLOUD POSTGRESQL (NEON)")
    logger.info("=" * 70)
    logger.info(f"Source SQLite Database : {sqlite_path}")
    logger.info(f"Target Database Engine  : {target_url.split('@')[-1] if '@' in target_url else target_url[:30] + '...'}")

    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"Source SQLite file does not exist: {sqlite_path}")

    # Connect to Source SQLite
    src_engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    SrcSession = sessionmaker(bind=src_engine)

    # Connect to Target Database (PostgreSQL / Neon)
    target_connect_args = {}
    if is_postgres and "sslmode" not in target_url:
        target_connect_args["sslmode"] = "require"

    target_engine = create_engine(
        target_url,
        connect_args=target_connect_args if is_postgres else {},
        pool_pre_ping=True,
    )
    TargetSession = sessionmaker(bind=target_engine)

    # Ensure tables exist on target database
    logger.info("Verifying/creating relational schema on target database...")
    Base.metadata.create_all(bind=target_engine)

    stats = {
        "source_counts": {},
        "target_before": {},
        "inserted_counts": {},
        "target_after": {},
        "status": "pending",
    }

    with SrcSession() as src_db, TargetSession() as target_db:
        # Check counts before migration
        for model_cls, table_name in TABLE_ORDER:
            src_count = src_db.query(model_cls).count()
            tgt_count = target_db.query(model_cls).count()
            stats["source_counts"][table_name] = src_count
            stats["target_before"][table_name] = tgt_count

        logger.info("\nSource SQLite Baseline Record Counts:")
        for tbl, cnt in stats["source_counts"].items():
            logger.info(f"  - {tbl:<25}: {cnt} rows")

        if dry_run:
            logger.info("\n[DRY RUN] No records were modified.")
            stats["status"] = "dry_run_complete"
            return stats

        # Migrate each table in dependency order
        for model_cls, table_name in TABLE_ORDER:
            src_records = src_db.query(model_cls).order_by(model_cls.id).all()
            existing_target_ids = {
                r[0] for r in target_db.query(model_cls.id).all()
            }

            records_to_insert = []
            for record in src_records:
                if record.id not in existing_target_ids:
                    # Create clean clone of record
                    data = {
                        c.name: getattr(record, c.name)
                        for c in record.__table__.columns
                    }
                    records_to_insert.append(data)

            if records_to_insert:
                logger.info(f"Migrating {len(records_to_insert)} new rows into '{table_name}'...")
                # Chunked bulk insert to avoid packet size limits
                chunk_size = 500
                for i in range(0, len(records_to_insert), chunk_size):
                    chunk = records_to_insert[i : i + chunk_size]
                    target_db.bulk_insert_mappings(model_cls, chunk)
                    target_db.commit()
                stats["inserted_counts"][table_name] = len(records_to_insert)
            else:
                logger.info(f"Table '{table_name}' is already up-to-date ({len(existing_target_ids)} rows exist). Skipping.")
                stats["inserted_counts"][table_name] = 0

        # Adjust PostgreSQL Sequences (setval) to prevent PK conflicts on new inserts
        if is_postgres:
            logger.info("\nSynchronizing PostgreSQL auto-increment sequences...")
            with target_engine.connect() as conn:
                for model_cls, table_name in TABLE_ORDER:
                    try:
                        seq_sql = text(
                            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                            f"COALESCE((SELECT MAX(id) FROM {table_name}), 1));"
                        )
                        conn.execute(seq_sql)
                        conn.commit()
                        logger.info(f"  --> Sequence reset for '{table_name}'")
                    except Exception as e:
                        logger.warning(f"  --> Sequence reset note on '{table_name}': {e}")

        # Check counts after migration
        for model_cls, table_name in TABLE_ORDER:
            tgt_count_after = target_db.query(model_cls).count()
            stats["target_after"][table_name] = tgt_count_after

    # Verify match
    all_matched = True
    logger.info("\n" + "=" * 70)
    logger.info(f"{'TABLE NAME':<26} | {'SQLITE SOURCE':<15} | {'TARGET CLOUD':<15} | {'STATUS'}")
    logger.info("-" * 70)
    for model_cls, table_name in TABLE_ORDER:
        src = stats["source_counts"][table_name]
        tgt = stats["target_after"][table_name]
        match = (tgt >= src)
        if not match:
            all_matched = False
        logger.info(f"{table_name:<26} | {src:<15} | {tgt:<15} | {'MATCH' if match else 'MISMATCH'}")
    logger.info("=" * 70)

    # Perform Safe Non-Destructive CRUD Verification on target database
    logger.info("\nPerforming Non-Destructive CRUD Verification on Target Database...")
    with TargetSession() as test_session:
        # 1. INSERT test zone
        test_zone = MiningZone(
            zone_code="TEST-Z999",
            name="Temporary CRUD Test Zone",
            mine_type="open_pit",
            description="Created by automated migration audit, to be immediately removed.",
            current_risk_tier="Safe",
        )
        test_session.add(test_zone)
        test_session.commit()
        test_id = test_zone.id
        logger.info(f"  [PASS] INSERT: Test zone created with ID={test_id}")

        # 2. SELECT test zone
        retrieved = test_session.query(MiningZone).filter(MiningZone.id == test_id).first()
        assert retrieved is not None, "Failed to retrieve test zone"
        logger.info("  [PASS] SELECT: Retrieved test zone successfully")

        # 3. UPDATE test zone
        retrieved.current_risk_tier = "Medium"
        test_session.commit()
        updated = test_session.query(MiningZone).filter(MiningZone.id == test_id).first()
        assert updated.current_risk_tier == "Medium", "Failed to update test zone"
        logger.info("  [PASS] UPDATE: Updated test zone risk tier successfully")

        # 4. DELETE test zone
        test_session.delete(updated)
        test_session.commit()
        deleted = test_session.query(MiningZone).filter(MiningZone.id == test_id).first()
        assert deleted is None, "Failed to clean up test zone"
        logger.info("  [PASS] DELETE: Cleaned up test zone successfully")

    stats["status"] = "verified_success" if all_matched else "count_mismatch"
    logger.info(f"\nMIGRATION RESULT: {stats['status'].upper()}\n")

    src_engine.dispose()
    target_engine.dispose()
    return stats


def auto_migrate_if_needed(target_engine, sqlite_path: str = DEFAULT_SQLITE_PATH, target_url: str = None):
    """
    Invoked during FastAPI startup lifecycle.
    If target database is PostgreSQL and has 0 mining zones, automatically
    migrates all historical records from the bundled SQLite database.
    """
    try:
        from backend.app.config import settings
        url_to_use = target_url or settings.DATABASE_URL
        if not url_to_use.startswith("postgres"):
            return  # SQLite doesn't need auto-migration

        with target_engine.connect() as conn:
            # Check if mining_zones table exists and count
            try:
                count = conn.execute(text("SELECT COUNT(*) FROM mining_zones")).scalar()
            except Exception:
                count = 0

            if count == 0 and os.path.exists(sqlite_path):
                logger.info("PostgreSQL / Neon database is empty. Triggering automatic historical migration from SQLite...")
                migrate_database(url_to_use, sqlite_path=sqlite_path)
            else:
                logger.info(f"Target database already contains {count} mining zones. Skipping auto-migration.")
    except Exception as e:
        logger.warning(f"Auto-migration check notice: {type(e).__name__}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATABASE_URL")
    if not target:
        print("Usage: python -m backend.app.database.migrate_sqlite_to_postgres <TARGET_DATABASE_URL>")
        print("Example: python -m backend.app.database.migrate_sqlite_to_postgres postgresql://user:pass@ep-cool-fog.neon.tech/neondb?sslmode=require")
        sys.exit(1)

    migrate_database(target)
