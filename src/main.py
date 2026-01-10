from pathlib import Path
from telemetry import load_telemetry


def main() -> None:
    csv_path = Path(__file__).parent.parent / "data" / "sample_trip.csv"
    telemetry = load_telemetry(csv_path)

    print(f"Loaded {len(telemetry)} telemetry samples")
    print("First 3 samples:")
    for t in telemetry[:3]:
        print(t)


if __name__ == "__main__":
    main()
