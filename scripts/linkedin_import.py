"""Autofill the wiki pages from a LinkedIn data export.

Usage:
    py scripts/linkedin_import.py <export.zip | extracted-folder>

Only text between <!-- BEGIN linkedin:<id> --> and <!-- END linkedin:<id> -->
is rewritten, so hand-written prose and project links survive re-runs.
"""

from __future__ import annotations

import csv
import sys
import tempfile
import zipfile
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "src" / "content" / "docs"

MONTHS = {
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
MONTH_NUMBERS = {name[:3].lower(): index for index, name in enumerate(MONTHS.values(), 1)}


def format_month(value: str) -> str:
    """Turn "Jan 2024" or "2024" into "January 2024" or "2024"."""
    parts = (value or "").strip().split()
    if len(parts) >= 2:
        return f"{MONTHS.get(parts[0][:3].lower(), parts[0])} {parts[-1]}"
    return " ".join(parts)


def format_period(start: str, end: str) -> str:
    begin = format_month(start)
    finish = format_month(end) or "Present"
    return f"{begin} – {finish}" if begin else finish


def date_key(value: str) -> tuple[int, int]:
    """Sort key; an empty end date means "current", so it sorts newest first."""
    parts = (value or "").strip().split()
    if not parts:
        return (9999, 12)
    year = int(parts[-1]) if parts[-1].isdigit() else 0
    month = MONTH_NUMBERS.get(parts[0][:3].lower(), 1) if len(parts) > 1 else 1
    return (year, month)


def read_rows(source: Path, name: str) -> list[dict[str, str]]:
    path = source / name
    if not path.exists():
        print(f"warn: {name} not found, skipping")
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def paragraphs(value: str) -> str:
    """LinkedIn descriptions are one line per bullet; keep them apart."""
    return "\n\n".join(line.strip() for line in (value or "").splitlines() if line.strip())


def entry(header: str, period: str, description: str = "") -> str:
    lines = [f"### {header}", "", f"**Period:** {period}"]
    if description:
        lines += ["", description]
    return "\n".join(lines)


def positions_body(rows: list[dict[str, str]]) -> str:
    def build(row: dict[str, str]) -> str:
        title = row.get("Title", "").strip()
        company = row.get("Company Name", "").strip()
        header = f"{title} — {company}" if company else title
        period = format_period(row.get("Started On", ""), row.get("Finished On", ""))
        return entry(header, period, paragraphs(row.get("Description", "")))

    rows = sorted(rows, key=lambda row: date_key(row.get("Finished On", "")), reverse=True)
    return "\n\n".join(build(row) for row in rows)


def education_body(rows: list[dict[str, str]]) -> str:
    def build(row: dict[str, str]) -> str:
        degree = row.get("Degree Name", "").strip()
        school = row.get("School Name", "").strip()
        header = f"{degree} — {school}" if degree else school
        period = format_period(row.get("Started On", ""), row.get("Finished On", ""))
        return entry(header, period)

    rows = sorted(rows, key=lambda row: date_key(row.get("Finished On", "")), reverse=True)
    return "\n\n".join(build(row) for row in rows)


def certifications_body(rows: list[dict[str, str]]) -> str:
    def build(row: dict[str, str]) -> str:
        name = row.get("Name", "").strip()
        authority = row.get("Authority", "").strip()
        header = f"{name} — {authority}" if authority else name
        # Certifications rarely expire: a missing end date means "issued", not "ongoing".
        start, end = row.get("Started On", ""), row.get("Finished On", "")
        period = format_period(start, end) if end.strip() else format_month(start)
        return entry(header, period)

    rows = sorted(rows, key=lambda row: date_key(row.get("Finished On", "")), reverse=True)
    return "\n\n".join(build(row) for row in rows)


def skills_body(rows: list[dict[str, str]]) -> str:
    unique: dict[str, str] = {}
    for row in rows:
        name = row.get("Name", "").strip()
        if name:
            unique.setdefault(name.casefold(), name)
    return "\n".join(f"- {unique[key]}" for key in sorted(unique))


def replace_block(path: Path, block_id: str, body: str, anchor: str) -> None:
    text = path.read_text(encoding="utf-8")
    begin = f"<!-- BEGIN linkedin:{block_id} -->"
    end = f"<!-- END linkedin:{block_id} -->"
    if begin in text and end in text:
        head = text.split(begin, 1)[0]
        tail = text.split(end, 1)[1]
        updated = f"{head}{begin}\n{body}\n{end}{tail}"
    elif anchor in text:
        head, rest = text.split(anchor, 1)
        updated = f"{head}{anchor}\n\n{begin}\n{body}\n{end}{rest}"
    else:
        print(f"warn: anchor {anchor!r} missing in {path.name}, skipping {block_id}")
        return
    path.write_text(updated, encoding="utf-8")
    print(f"updated {path.relative_to(DOCS.parent.parent.parent)} ({block_id})")


def find_csv_root(base: Path) -> Path:
    if (base / "Profile.csv").exists():
        return base
    for candidate in base.rglob("Profile.csv"):
        return candidate.parent
    return base


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2].strip())
        return 2

    raw = Path(argv[1]).expanduser()
    with tempfile.TemporaryDirectory(prefix="linkedin-export-") as temp:
        if raw.is_dir():
            source = raw
        elif raw.is_file() and raw.suffix.lower() == ".zip":
            with zipfile.ZipFile(raw) as archive:
                archive.extractall(temp)
            source = Path(temp)
        else:
            print(f"error: {raw} is not a folder or a .zip file")
            return 2
        source = find_csv_root(source)

        replace_block(
            DOCS / "experience.md",
            "education",
            education_body(read_rows(source, "Education.csv")),
            "## Education",
        )
        replace_block(
            DOCS / "experience.md",
            "certification",
            certifications_body(read_rows(source, "Certifications.csv")),
            "## Certification",
        )
        replace_block(
            DOCS / "experience.md",
            "work",
            positions_body(read_rows(source, "Positions.csv")),
            "## Work",
        )
        replace_block(
            DOCS / "skills.md",
            "skills",
            skills_body(read_rows(source, "Skills.csv")),
            "## From LinkedIn",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
