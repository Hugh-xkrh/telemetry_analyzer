from pathlib import Path
from .detectors import detect_coolant_overheat, detect_rpm_instability, rpm_instaility_config
from .telemetry import load_telemetry


def main() -> None:
    header_line_marker = "-" * 10
    csv_path = Path(__file__).parent.parent / "data" / "sample_trip.csv"
    telemetry = load_telemetry(csv_path)

    print(f"Loaded {len(telemetry)} telemetry samples")
    print(f"{header_line_marker}First 3 samples:{header_line_marker}")
    for t in telemetry[:3]:
        print(t)

    events = detect_coolant_overheat(telemetry, threshold_c=130.0)

    print(f"{header_line_marker}Overheat events: {len(events)}{header_line_marker}")
    for e in events:
        print(e)


if __name__ == "__main__":
    main()
