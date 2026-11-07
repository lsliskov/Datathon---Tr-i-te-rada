from __future__ import annotations

import calendar
import csv
import difflib
import html
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


COUNTIES = (
    "Bjelovarsko-bilogorska županija",
    "Brodsko-posavska županija",
    "Dubrovačko-neretvanska županija",
    "Grad Zagreb",
    "Istarska županija",
    "Karlovačka županija",
    "Koprivničko-križevačka županija",
    "Krapinsko-zagorska županija",
    "Ličko-senjska županija",
    "Međimurska županija",
    "Osječko-baranjska županija",
    "Požeško-slavonska županija",
    "Primorsko-goranska županija",
    "Sisačko-moslavačka županija",
    "Splitsko-dalmatinska županija",
    "Šibensko-kninska županija",
    "Varaždinska županija",
    "Virovitičko-podravska županija",
    "Vukovarsko-srijemska županija",
    "Zadarska županija",
    "Zagrebačka županija",
)

ZAGREB_REGION = "Zagrebačka županija + Grad Zagreb"

HZZ_FEED_REGIONS = {
    1: "Bjelovarsko-bilogorska županija",
    2: "Brodsko-posavska županija",
    3: "Dubrovačko-neretvanska županija",
    4: "Grad Zagreb",
    5: "Istarska županija",
    6: "Karlovačka županija",
    7: "Koprivničko-križevačka županija",
    8: "Krapinsko-zagorska županija",
    9: "Ličko-senjska županija",
    10: "Međimurska županija",
    11: "Osječko-baranjska županija",
    12: "Požeško-slavonska županija",
    13: "Primorsko-goranska županija",
    14: "Sisačko-moslavačka županija",
    15: "Splitsko-dalmatinska županija",
    16: "Šibensko-kninska županija",
    17: "Varaždinska županija",
    18: "Virovitičko-podravska županija",
    19: "Vukovarsko-srijemska županija",
    20: "Zadarska županija",
    21: "Zagrebačka županija",
}

REGION_COORDINATES = {
    "Bjelovarsko-bilogorska županija": (45.90, 16.84),
    "Brodsko-posavska županija": (45.16, 18.02),
    "Dubrovačko-neretvanska županija": (42.65, 18.09),
    "Istarska županija": (45.23, 13.94),
    "Karlovačka županija": (45.49, 15.55),
    "Koprivničko-križevačka županija": (46.16, 16.83),
    "Krapinsko-zagorska županija": (46.16, 15.87),
    "Ličko-senjska županija": (44.55, 15.37),
    "Međimurska županija": (46.38, 16.43),
    "Osječko-baranjska županija": (45.55, 18.69),
    "Požeško-slavonska županija": (45.34, 17.68),
    "Primorsko-goranska županija": (45.33, 14.44),
    "Sisačko-moslavačka županija": (45.49, 16.37),
    "Splitsko-dalmatinska županija": (43.51, 16.44),
    "Šibensko-kninska županija": (43.74, 15.89),
    "Varaždinska županija": (46.31, 16.34),
    "Virovitičko-podravska županija": (45.83, 17.38),
    "Vukovarsko-srijemska županija": (45.29, 18.80),
    "Zadarska županija": (44.12, 15.23),
    "Zagrebačka županija + Grad Zagreb": (45.82, 16.10),
}


@dataclass(frozen=True)
class DashboardData:
    regional: pd.DataFrame
    occupations: pd.DataFrame
    sectors: pd.DataFrame
    history: pd.DataFrame
    permit_date: date
    population_year: int
    hzz_date: date | None
    source_files: tuple[str, ...]


def _ascii_key(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold().replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def canonical_region(value: Any) -> str | None:
    key = _ascii_key(value)
    key = re.sub(r"\s+zupanija$", "", key)
    county_keys = {
        re.sub(r"\s+zupanija$", "", _ascii_key(county)): county
        for county in COUNTIES
    }
    if key in county_keys:
        return county_keys[key]
    close_match = difflib.get_close_matches(
        key, county_keys.keys(), n=1, cutoff=0.84
    )
    if close_match:
        return county_keys[close_match[0]]
    for county in COUNTIES:
        county_key = re.sub(r"\s+zupanija$", "", _ascii_key(county))
        if key == county_key:
            return county
    if key in {"grad zagreb", "zagreb grad"}:
        return "Grad Zagreb"
    if key in {"zagreb", "zagrebacka zagreb"}:
        return "Zagrebačka županija"
    return None


def combined_region(value: Any) -> str | None:
    region = canonical_region(value)
    if region in {"Grad Zagreb", "Zagrebačka županija"}:
        return ZAGREB_REGION
    return region


def parse_report_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    match = re.fullmatch(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", text)
    if match:
        day, month, year = map(int, match.groups())
        return date(year, month, day)
    match = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if match:
        first, second, third = map(int, match.groups())
        if second > 12:
            return date(first, third, second)
        return date(first, second, third)
    return None


def _report_date_from_filename(path: Path) -> date | None:
    stem = _ascii_key(path.stem)
    year_match = re.search(r"(20\d{2})", stem)
    if not year_match:
        return None
    months = {
        "sijecanj": 1,
        "sijeanj": 1,
        "veljaca": 2,
        "ozujak": 3,
        "oujak": 3,
        "travanj": 4,
        "svibanj": 5,
        "lipanj": 6,
        "srpanj": 7,
        "kolovoz": 8,
        "rujan": 9,
        "listopad": 10,
        "studeni": 11,
        "prosinac": 12,
    }
    month = next((value for name, value in months.items() if name in stem), None)
    if month is None:
        return None
    year = int(year_match.group(1))
    return date(year, month, calendar.monthrange(year, month)[1])


def calculate_pressure_index(regional: pd.DataFrame) -> pd.DataFrame:
    result = regional.copy()
    result["oglasi_na_1000"] = (
        result["hzz_oglasi"] / result["stanovnici"] * 1000
    )
    result["dozvole_na_1000"] = (
        result["mup_dozvole"] / result["stanovnici"] * 1000
    )

    for source, target in (
        ("oglasi_na_1000", "ocjena_potraznje"),
        ("dozvole_na_1000", "ocjena_dozvola"),
    ):
        values = result[source]
        minimum = values.min()
        maximum = values.max()
        if pd.isna(minimum) or pd.isna(maximum):
            result[target] = float("nan")
        elif maximum == minimum:
            result[target] = 50.0
        else:
            result[target] = (values - minimum) / (maximum - minimum) * 100

    result["indeks_pritiska"] = result[
        ["ocjena_potraznje", "ocjena_dozvola"]
    ].mean(axis=1)
    return result.sort_values("indeks_pritiska", ascending=False).reset_index(
        drop=True
    )


def _read_population(path: Path) -> tuple[dict[str, int], int]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="cp1250")

    delimiter = ";" if text[:4096].count(";") > text[:4096].count(",") else ","
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    header_index = next(
        (i for i, row in enumerate(rows) if row and _ascii_key(row[0]) == "starost"),
        None,
    )
    if header_index is None or header_index + 1 >= len(rows):
        raise ValueError(f"Nije pronađeno zaglavlje tablice stanovništva: {path.name}")

    headers = rows[header_index]
    totals = rows[header_index + 1]
    if _ascii_key(totals[0]) != "ukupno":
        raise ValueError(f"Nije pronađen ukupni red stanovništva: {path.name}")

    population: dict[str, int] = {}
    years: list[int] = []
    for index, heading in enumerate(headers):
        match = re.fullmatch(r"\s*(20\d{2})\s+(.+?)\s+Svega\s*", heading)
        if not match:
            continue
        year = int(match.group(1))
        region = canonical_region(match.group(2))
        if region is not None:
            years.append(year)
    if not years:
        raise ValueError(f"Nisu pronađeni podaci po županijama: {path.name}")
    latest_year = max(years)

    for index, heading in enumerate(headers):
        match = re.fullmatch(r"\s*(20\d{2})\s+(.+?)\s+Svega\s*", heading)
        if not match or int(match.group(1)) != latest_year or index >= len(totals):
            continue
        region = canonical_region(match.group(2))
        if region is None:
            continue
        value = _number(totals[index])
        if value is not None:
            population[region] = int(value)
    return population, latest_year


def _number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("\xa0", "").replace(" ", "")
    if not text:
        return None
    text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _plain_description(value: str) -> str:
    text = value or ""
    for _ in range(2):
        text = html.unescape(text)
    return re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ").strip()


def _extract_category(description: str) -> str:
    match = re.search(
        r"Kategorija\s*:\s*(.*?)(?=,\s*(?:Rok|Mjesto|Op|upanija)|$)",
        description,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return "Nerazvrstano"
    category = re.sub(r"\s+", " ", match.group(1)).strip(" ,.;")
    return category or "Nerazvrstano"


def _extract_county(description: str) -> str | None:
    match = re.search(
        r"(?:Županija|Zupanija)\s*:\s*([^,;<]+)",
        description,
        flags=re.IGNORECASE,
    )
    return canonical_region(match.group(1)) if match else None


def _read_occupation_categories(path: Path) -> tuple[dict[str, str], list[str]]:
    categories_by_id: dict[str, str] = {}
    categories: set[str] = set()
    for file in sorted(path.glob("rsskat*.xml")):
        items = ET.parse(file).getroot().findall(".//item")
        labels = [
            _extract_category(_plain_description(item.findtext("description") or ""))
            for item in items
        ]
        labels = [label for label in labels if label != "Nerazvrstano"]
        if not labels:
            continue
        feed_category = Counter(labels).most_common(1)[0][0]
        categories.add(feed_category)
        for item in items:
            identifier = (
                item.findtext("guid") or item.findtext("link") or ""
            ).strip()
            if identifier:
                categories_by_id.setdefault(identifier, feed_category)
    return categories_by_id, sorted(categories)


def _canonical_occupation(value: str, categories: list[str]) -> str:
    key = _ascii_key(value)
    if not key or key == "nerazvrstano":
        return "Nerazvrstano"
    category_keys = {_ascii_key(category): category for category in categories}
    if key in category_keys:
        return category_keys[key]
    matches = [
        category
        for normalized, category in category_keys.items()
        if len(key) >= 8 and normalized.startswith(key)
    ]
    return matches[0] if len(matches) == 1 else "Nerazvrstano"


def _read_hzz(
    path: Path, occupation_path: Path
) -> tuple[pd.DataFrame, date | None]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    latest_date: date | None = None
    category_by_id, categories = _read_occupation_categories(occupation_path)

    for file in sorted(path.glob("rsszup*.xml")):
        match = re.fullmatch(r"rsszup(\d+)\.xml", file.name, re.IGNORECASE)
        feed_id = int(match.group(1)) if match else 1000
        feed_region = HZZ_FEED_REGIONS.get(feed_id)
        if feed_region is None:
            continue
        root = ET.parse(file).getroot()
        for item in root.findall(".//item"):
            description = _plain_description(item.findtext("description") or "")
            county = _extract_county(description) or feed_region
            region = combined_region(county)
            if region is None:
                continue
            published = parse_report_date(item.findtext("pubDate"))
            if published and (latest_date is None or published > latest_date):
                latest_date = published
            guid = (
                item.findtext("guid")
                or item.findtext("link")
                or f"{item.findtext('subject') or item.findtext('title')}|{published}"
            ).strip()
            key = (region, guid)
            if key in seen:
                continue
            seen.add(key)

            occupation = category_by_id.get(guid)
            if occupation is None:
                occupation = _canonical_occupation(
                    _extract_category(description), categories
                )
            title = (
                item.findtext("subject")
                or item.findtext("title")
                or occupation
                or "Naziv nije naveden"
            ).strip()
            records.append(
                {
                    "regija": region,
                    "zanimanje": occupation,
                    "naziv_oglasa": title,
                    "datum_objave": published,
                }
            )

    if not records:
        raise ValueError(f"Nisu pronađeni HZZ oglasi u direktoriju: {path}")
    return pd.DataFrame.from_records(records), latest_date


def _read_permit_report(path: Path) -> dict[str, Any]:
    sheet = pd.read_excel(path, header=None, dtype=object, engine="openpyxl")
    if sheet.empty or sheet.shape[1] < 2:
        raise ValueError(f"Prazna ili neispravna MUP tablica: {path.name}")

    activity_header = next(
        (
            index
            for index, row in sheet.iterrows()
            if len(row) and _ascii_key(row.iloc[0]) == "djelatnosti"
        ),
        None,
    )
    if activity_header is None:
        raise ValueError(f"Nije pronađen naslov MUP tablice: {path.name}")
    report_date = parse_report_date(sheet.iat[activity_header, 1])
    if report_date is None:
        report_date = _report_date_from_filename(path)
    if report_date is None:
        raise ValueError(f"Nije prepoznat datum MUP izvještaja: {path.name}")

    sectors: list[dict[str, Any]] = []
    for _, row in sheet.iloc[activity_header + 1 :].iterrows():
        label = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ""
        key = _ascii_key(label)
        if key == "drzavljanstvo":
            break
        value = _number(row.iloc[1]) if len(row) > 1 else None
        if (
            label
            and key not in {"djelatnosti", "top 5 djelatnosti", "ukupno"}
            and value is not None
        ):
            sectors.append({"djelatnost": label, "dozvole": int(value)})

    county_header = next(
        (
            index
            for index, row in sheet.iterrows()
            if (
                "produljenje" in {_ascii_key(value) for value in row}
                and "ukupno" in {_ascii_key(value) for value in row}
                and any(
                    _ascii_key(value).startswith("sezonsko")
                    for value in row
                )
            )
        ),
        None,
    )
    if county_header is None:
        raise ValueError(f"Nije pronađena tablica policijskih uprava: {path.name}")

    total_column = next(
        index
        for index, value in enumerate(sheet.iloc[county_header])
        if _ascii_key(value) == "ukupno"
    )
    permits: dict[str, int] = {}
    for row_index in range(county_header + 1, len(sheet)):
        row = sheet.iloc[row_index]
        raw_region = row.iloc[0] if len(row) else None
        if raw_region is None or pd.isna(raw_region):
            continue
        region_key = _ascii_key(raw_region)
        if region_key == "ukupno":
            break
        region = combined_region(raw_region)
        if region is None:
            continue
        amount = _number(row.iloc[total_column])
        if amount is not None:
            permits[region] = permits.get(region, 0) + int(amount)

    if not permits:
        raise ValueError(f"Nisu pronađene dozvole po policijskim upravama: {path.name}")
    return {
        "date": report_date,
        "sectors": sectors,
        "permits": permits,
        "total": sum(permits.values()),
        "file": path.name,
    }


def _combine_values(values: dict[str, int]) -> dict[str, int]:
    combined: dict[str, int] = {}
    for region, value in values.items():
        target = combined_region(region)
        if target is not None:
            combined[target] = combined.get(target, 0) + value
    return combined


def build_dashboard_data(data_root: Path) -> DashboardData:
    population_dir = data_root / "stanovništvo"
    permit_dir = data_root / "dozvole"
    hzz_dir = data_root / "poslovi po županijama"
    occupation_dir = data_root / "poslovi po zanimanju"
    population_files = sorted(population_dir.glob("DE_SP22*.csv"))
    permit_files = sorted(permit_dir.glob("*.xlsx"))
    if not population_files:
        raise FileNotFoundError(f"Nedostaje CSV stanovništva u {population_dir}")
    if not permit_files:
        raise FileNotFoundError(f"Nedostaju MUP Excel izvještaji u {permit_dir}")
    if not hzz_dir.is_dir():
        raise FileNotFoundError(f"Nedostaje HZZ direktorij {hzz_dir}")
    if not occupation_dir.is_dir():
        raise FileNotFoundError(f"Nedostaje HZZ direktorij {occupation_dir}")

    population, population_year = _read_population(population_files[0])
    population = _combine_values(population)
    vacancies, hzz_date = _read_hzz(hzz_dir, occupation_dir)
    reports = [
        _read_permit_report(file)
        for file in permit_files
    ]
    reports.sort(key=lambda item: item["date"])
    latest = reports[-1]
    permit_values = latest["permits"]

    hzz_counts = vacancies.groupby("regija").size().to_dict()
    regions = sorted(set(population) | set(hzz_counts) | set(permit_values))
    regional = pd.DataFrame(
        [
            {
                "regija": region,
                "stanovnici": population.get(region),
                "hzz_oglasi": int(hzz_counts.get(region, 0)),
                "mup_dozvole": permit_values.get(region),
            }
            for region in regions
        ]
    )
    regional = regional.dropna(subset=["stanovnici", "mup_dozvole"])
    if regional.empty:
        raise ValueError(
            "HZZ, MUP i DZS podaci nemaju zajedničke regionalne jedinice."
        )
    regional["stanovnici"] = regional["stanovnici"].astype(int)
    regional["mup_dozvole"] = regional["mup_dozvole"].astype(int)
    regional = calculate_pressure_index(regional)

    occupation_counts = (
        vacancies.groupby(["regija", "zanimanje"], as_index=False)
        .size()
        .rename(columns={"size": "oglasi"})
        .sort_values("oglasi", ascending=False)
    )
    sectors = pd.DataFrame(latest["sectors"])
    if sectors.empty:
        raise ValueError(f"Nema podataka o djelatnostima u {latest['file']}")
    sectors = sectors.sort_values("dozvole", ascending=False)

    history = pd.DataFrame(
        [
            {
                "datum": report["date"],
                "godina": report["date"].year,
                "izdane_dozvole": report["total"],
            }
            for report in reports
        ]
    ).sort_values("datum")
    history["godina"] = history["godina"].astype(str)
    return DashboardData(
        regional=regional,
        occupations=occupation_counts,
        sectors=sectors,
        history=history,
        permit_date=latest["date"],
        population_year=population_year,
        hzz_date=hzz_date,
        source_files=(
            population_files[0].name,
            latest["file"],
            f"{len(list(hzz_dir.glob('rsszup*.xml')))} HZZ XML datoteka",
        ),
    )


@st.cache_data(show_spinner="Učitavam HZZ, MUP i DZS podatke…")
def load_dashboard_data(data_root: str) -> DashboardData:
    return build_dashboard_data(Path(data_root))


def format_number(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", ".")
