from pathlib import Path
from .detectors import detect_coolant_overheat
from .telemetry import load_telemetry


def main() -> None:
    csv_path = Path(__file__).parent.parent / "data" / "sample_trip.csv"
    telemetry = load_telemetry(csv_path)

    print(f"Loaded {len(telemetry)} telemetry samples")
    print("First 3 samples:")
    for t in telemetry[:3]:
        print(t)

    events = detect_coolant_overheat(telemetry, threshold_c=130.0)

    print(f"Overheat events: {len(events)}")
    for e in events:
        print(e)


if __name__ == "__main__":
    main()
