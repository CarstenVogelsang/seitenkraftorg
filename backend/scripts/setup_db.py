#!/usr/bin/env python3
"""
Database Setup Script for seitenkraft.org

This script initializes the Supabase database schema and optionally loads
sample data. It reads the SQL schema from backend/app/db/supabase_schema.sql
and executes it against your Supabase instance.

Usage:
    python backend/scripts/setup_db.py

Environment Variables Required:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_KEY - Your Supabase service role key (not anon key!)

Optional Arguments:
    --skip-sample-data - Skip inserting sample data
    --drop-tables - Drop existing tables before creating (DESTRUCTIVE!)
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nPlease install required packages:")
    print("  pip install psycopg2-binary python-dotenv")
    print("  # or with poetry:")
    print("  poetry add psycopg2-binary python-dotenv")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {message}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {message}")


def load_environment():
    """Load environment variables from .env file"""
    # Try loading from backend/.env first, then root .env
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print_info(f"Loaded environment from: {env_path}")
            return

    print_warning("No .env file found, using system environment variables")


def get_db_connection_string() -> str:
    """
    Build PostgreSQL connection string from Supabase URL

    Converts: https://xxxxx.supabase.co
    To: postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable not set")

    if not supabase_key:
        raise ValueError("SUPABASE_KEY environment variable not set")

    # Note: For direct PostgreSQL connection, you need the database password,
    # not the anon/service key. This should be in SUPABASE_DB_PASSWORD
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    if not db_password:
        print_error("SUPABASE_DB_PASSWORD environment variable not set")
        print_info("You need the direct database password, not the API key")
        print_info("Find it in: Supabase Dashboard → Settings → Database → Connection string")
        raise ValueError("SUPABASE_DB_PASSWORD required for direct database connection")

    # Extract project reference from URL
    # e.g., https://xxxxx.supabase.co -> xxxxx
    if "supabase.co" in supabase_url:
        project_ref = supabase_url.split("//")[1].split(".")[0]
        db_host = f"db.{project_ref}.supabase.co"
    else:
        raise ValueError(f"Invalid SUPABASE_URL format: {supabase_url}")

    connection_string = f"postgresql://postgres:{db_password}@{db_host}:5432/postgres"
    return connection_string


def get_db_connection():
    """Create database connection"""
    try:
        connection_string = get_db_connection_string()
        conn = psycopg2.connect(connection_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print_success("Connected to Supabase database")
        return conn
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        raise


def load_schema_sql() -> str:
    """Load SQL schema from file"""
    schema_path = Path(__file__).parent.parent / "app" / "db" / "supabase_schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print_success(f"Loaded schema from: {schema_path}")
    return sql_content


def drop_tables(cursor):
    """Drop all tables (DESTRUCTIVE!)"""
    print_warning("Dropping existing tables...")

    drop_commands = [
        "DROP TABLE IF EXISTS domain_registrierung CASCADE;",
        "DROP TABLE IF EXISTS domains_tld_registrar CASCADE;",
        "DROP TABLE IF EXISTS domains_tld CASCADE;",
        "DROP TABLE IF EXISTS kunden CASCADE;",
        "DROP FUNCTION IF EXISTS update_aktualisiert_am() CASCADE;",
    ]

    for cmd in drop_commands:
        try:
            cursor.execute(cmd)
            print_info(f"  Dropped: {cmd.split()[4]}")
        except Exception as e:
            print_warning(f"  Could not drop: {e}")


def execute_schema(cursor, sql_content: str, skip_sample_data: bool = False):
    """Execute SQL schema"""
    if skip_sample_data:
        # Remove sample data section
        if "-- Sample Data (for testing)" in sql_content:
            sql_content = sql_content.split("-- Sample Data (for testing)")[0]
            print_info("Skipping sample data insertion")

    try:
        cursor.execute(sql_content)
        print_success("Schema executed successfully")
    except Exception as e:
        print_error(f"Failed to execute schema: {e}")
        raise


def verify_setup(cursor):
    """Verify that tables were created"""
    print_header("Verifying Setup")

    # Check tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()

    if not tables:
        print_error("No tables found!")
        return False

    print_success(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"  • {table[0]}")

    # Check row counts
    print("\n" + Colors.BOLD + "Row counts:" + Colors.ENDC)

    table_names = ['kunden', 'domains_tld', 'domains_tld_registrar', 'domain_registrierung']
    for table_name in table_names:
        try:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                sql.Identifier(table_name)
            ))
            count = cursor.fetchone()[0]
            print(f"  • {table_name}: {count} rows")
        except Exception as e:
            print_warning(f"  • {table_name}: Could not count - {e}")

    return True


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Supabase database schema for seitenkraft.org"
    )
    parser.add_argument(
        "--skip-sample-data",
        action="store_true",
        help="Skip inserting sample data"
    )
    parser.add_argument(
        "--drop-tables",
        action="store_true",
        help="Drop existing tables before creating (DESTRUCTIVE!)"
    )

    args = parser.parse_args()

    print_header("seitenkraft.org - Database Setup")

    # Load environment
    load_environment()

    # Warning for destructive operation
    if args.drop_tables:
        print_warning("⚠️  WARNING: --drop-tables will delete all existing data!")
        response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print_info("Aborted.")
            return

    try:
        # Connect to database
        print_header("Connecting to Database")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Drop tables if requested
        if args.drop_tables:
            print_header("Dropping Existing Tables")
            drop_tables(cursor)

        # Load schema
        print_header("Loading Schema")
        sql_content = load_schema_sql()

        # Execute schema
        print_header("Executing Schema")
        execute_schema(cursor, sql_content, skip_sample_data=args.skip_sample_data)

        # Verify
        verify_setup(cursor)

        # Close connection
        cursor.close()
        conn.close()

        print_header("✅ Database Setup Complete!")
        print_success("Your Supabase database is ready to use")
        print_info("Next steps:")
        print("  1. Start the FastAPI backend: cd backend && uvicorn app.main:app --reload")
        print("  2. Start the React frontend: cd frontend && npm run dev")

    except Exception as e:
        print_header("❌ Setup Failed")
        print_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
