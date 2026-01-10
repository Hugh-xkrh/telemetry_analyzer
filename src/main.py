from pathlib import Path
import csv


def load_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main() -> None:
    csv_path = Path(__file__).parent.parent / "data" / "sample_trip.csv"
    rows = load_csv(csv_path)

    print("Loaded:", csv_path)
    print("Row count:", len(rows))
    print("Columns:", list(rows[0].keys()) if rows else [])
    print("First 5 rows:")
    for r in rows[:5]:
        print(r)


if __name__ == "__main__":
    main()
