from app.database.connection import create_database
from app.models import Activity


def main() -> None:
    create_database()
    print("Kairos database initialized.")


if __name__ == "__main__":
    main()