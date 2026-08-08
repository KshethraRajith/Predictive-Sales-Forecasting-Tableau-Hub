"""Helpers to prepare CSV outputs consumable by Tableau.

This module writes forecast and aggregated outputs into an `output/` folder which
Tableau can connect to as a flat-file data source. For more advanced workflows,
consider using the Tableau Hyper API to create .hyper extracts.
"""
import os
import shutil


def publish_csv_to_output(src_path: str, dest_name: str = None, output_dir: str = "output/tableau") -> str:
    os.makedirs(output_dir, exist_ok=True)
    if dest_name is None:
        dest_name = os.path.basename(src_path)
    dest_path = os.path.join(output_dir, dest_name)
    shutil.copy(src_path, dest_path)
    return dest_path


if __name__ == "__main__":
    print("Utility module for exporting CSVs to output/tableau")
