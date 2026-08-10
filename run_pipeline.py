from pathlib import Path

from f1_data.jolpica import JolpicaClient
from f1_data.storage import write_parquet
from f1_data.transformers import races_to_records


def main() -> None:
    client = JolpicaClient()

    races = client.get_races(2026)

    records = races_to_records(races)

    output_path = Path("data/processed/2026/races.parquet")

    write_parquet(records, output_path)

    print(f"Written {len(records)} races to {output_path}")


if __name__ == "__main__":
    main()