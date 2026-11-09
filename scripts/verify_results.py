"""Verifikasi input dan hasil eksperimen pendahuluan 100.000 event."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "artifacts" / "replay-inputs" / "20250101_event_datetime_sample100k"
RUNS = ROOT / "artifacts" / "runs"
COMPRESSION = {60, 288, 1440}
CLIENTS = {1, 4, 8}
EXPECTED_ROWS = 100_000


def sha256_file(path: Path) -> str:
    """Hitung SHA-256 isi berkas.

    Args:
        path: Berkas yang diperiksa.

    Returns:
        Digest heksadesimal SHA-256.

    Raises:
        FileNotFoundError: Berkas tidak ditemukan.
    """
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_input() -> None:
    """Periksa jumlah baris dan checksum input dari manifest.

    Raises:
        ValueError: Profil atau checksum input tidak sesuai.
    """
    manifest = json.loads((INPUT / "manifest.json").read_text(encoding="utf-8"))
    chunks = manifest["chunks"]
    if manifest["row_count"] != EXPECTED_ROWS or len(chunks) != 10:
        raise ValueError("Jumlah event atau chunk input tidak sesuai")
    if manifest["distinct_trip_ids"] != EXPECTED_ROWS:
        raise ValueError("ID perjalanan pada input tidak unik")
    if sum(chunk["rows"] for chunk in chunks) != EXPECTED_ROWS:
        raise ValueError("Jumlah baris per chunk tidak sesuai")
    for chunk in chunks:
        if sha256_file(INPUT / chunk["file"]) != chunk["sha256"]:
            raise ValueError(f"Checksum input berbeda: {chunk['file']}")
    for line in (INPUT / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        expected, name = line.split(maxsplit=1)
        if sha256_file(INPUT / name) != expected:
            raise ValueError(f"Checksum manifest berbeda: {name}")


def verify_runs() -> None:
    """Periksa 18 hasil valid dan tampilkan median setiap konfigurasi.

    Raises:
        ValueError: Matriks, jumlah baris, atau status hasil tidak sesuai.
    """
    seen: set[tuple[str, int, int]] = set()
    paths = sorted(RUNS.glob("*/validation/metrics-summary.json"))
    if len(paths) != 18:
        raise ValueError(f"Ditemukan {len(paths)} run, seharusnya 18")
    for path in paths:
        metric = json.loads(path.read_text(encoding="utf-8"))
        engine = "tidb" if metric["engine"].startswith("TiDB") else "postgres"
        key = (engine, int(metric["c"]), int(metric.get("k", metric.get("concurrency"))))
        if key in seen or key[1] not in COMPRESSION or key[2] not in CLIENTS:
            raise ValueError(f"Konfigurasi ganda atau tidak dikenal: {path}")
        if (metric["status"] != "PASS" or metric["input_rows"] != EXPECTED_ROWS
                or metric["query_error"] != 0 or metric["query_success"] <= 0):
            raise ValueError(f"Run tidak lulus pemeriksaan dasar: {path}")
        profile = metric.get("target_profile")
        if profile is not None and (profile["row_count"] != EXPECTED_ROWS
                                    or profile["distinct_trip_ids"] != EXPECTED_ROWS):
            raise ValueError(f"Target tidak lengkap: {path}")
        if engine == "tidb" and (metric.get("replica_available") != 1
                                  or metric.get("replica_progress") != 1):
            raise ValueError(f"TiFlash belum siap: {path}")
        seen.add(key)
        print(f"{engine:8} c={key[1]:4} k={key[2]} median={metric['median_latency_ms']:.3f} ms")
    expected = {(engine, c, k) for engine in ("tidb", "postgres")
                for c in COMPRESSION for k in CLIENTS}
    if seen != expected:
        raise ValueError(f"Matriks tidak lengkap: {expected - seen}")


def main() -> None:
    """Jalankan pemeriksaan tanpa mengubah artefak.

    Raises:
        ValueError: Artefak tidak memenuhi pemeriksaan.
        FileNotFoundError: Ada berkas yang hilang.
    """
    verify_input()
    verify_runs()
    print("PASS: checksum input dan 18 konfigurasi terverifikasi")


if __name__ == "__main__":
    main()
