#!/usr/bin/env python3
"""Compatibility helper: rebuild product_catalog.json from the local registry."""
from pathlib import Path
from llocg_update_database import write_product_catalog_from_registry

ROOT = Path(__file__).resolve().parent
DBDIR = ROOT / "llocg_db_out_full"

if __name__ == "__main__":
    write_product_catalog_from_registry(
        DBDIR / "product_release_registry.json",
        DBDIR / "product_catalog.json",
    )
