#!/usr/bin/env python3
"""Build RenderCV variants from the tagged master CV source."""

from __future__ import annotations

import argparse
import copy
import os
import re
from datetime import date
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "cv" / "master" / "jesus_erro_cv_master.yaml"
GENERATED_DIR = ROOT / "cv" / "generated"
VARIANTS = ("full", "it", "it_core", "ita", "mechanics")
OUTPUT_FILES = {
    "full": GENERATED_DIR / "jesus_erro_cv_full.yaml",
    "it": GENERATED_DIR / "jesus_erro_cv_it.yaml",
    "it_core": GENERATED_DIR / "jesus_erro_cv_it_core.yaml",
    "ita": GENERATED_DIR / "jesus_erro_cv_ita.yaml",
    "mechanics": GENERATED_DIR / "jesus_erro_cv_mechanics.yaml",
}
ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")
HELPER_KEYS = {"targets"}
LEGACY_CV_DIR = ROOT / "cv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "variants",
        nargs="*",
        choices=VARIANTS,
        help="Variants to build. Defaults to all variants.",
    )
    return parser.parse_args()


def load_master() -> dict:
    with MASTER_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "CV_BIRTH_DATE must use ISO format YYYY-MM-DD "
            f"(received: {value!r})"
        ) from exc


def format_spanish_age(birth_date: date, today: date) -> str:
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    if today.day < birth_date.day:
        months -= 1

    years, remaining_months = divmod(months, 12)
    years_label = "year" if years == 1 else "years"
    months_label = "month" if remaining_months == 1 else "months"
    return f"({years} {years_label} & {remaining_months} {months_label})"


def build_dynamic_env() -> dict[str, str]:
    env = dict(os.environ)
    birth_date_raw = env.get("CV_BIRTH_DATE")
    if not birth_date_raw:
        return env

    birth_date = parse_iso_date(birth_date_raw)
    age_text = format_spanish_age(birth_date, date.today())
    env["CV_AGE"] = age_text
    env["CV_BIRTH_DATE_WITH_AGE"] = f"{birth_date_raw} {age_text}"
    return env


def substitute_env(value, env: dict[str, str]):
    if isinstance(value, dict):
        return {key: substitute_env(item, env) for key, item in value.items()}
    if isinstance(value, list):
        return [substitute_env(item, env) for item in value]
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in env:
                raise KeyError(f"Missing environment variable: {name}")
            return env[name]

        return ENV_PATTERN.sub(replace, value)
    return value


def resolve_relative_asset(path_value: str, target_dir: Path) -> str:
    if not path_value or "://" in path_value:
        return path_value

    path = Path(path_value)
    if path.is_absolute():
        return path_value

    candidates = [
        MASTER_PATH.parent / path,
        LEGACY_CV_DIR / path,
        ROOT / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return os.path.relpath(candidate, target_dir)

    return path_value


def include_entry(entry, variant: str) -> bool:
    if isinstance(entry, dict):
        targets = entry.get("targets")
        if targets is not None:
            return variant in targets
    return True


def strip_helper_fields(entry):
    if isinstance(entry, dict):
        entry = {key: strip_helper_fields(value) for key, value in entry.items() if key not in HELPER_KEYS}
        if set(entry.keys()) == {"text"}:
            return entry["text"]
        return entry
    if isinstance(entry, list):
        return [strip_helper_fields(item) for item in entry]
    return entry


def build_variant(master: dict, variant: str) -> dict:
    rendered = substitute_env(copy.deepcopy(master), build_dynamic_env())
    variant_meta = rendered.get("meta", {}).get("variants", {}).get(variant, {})
    cv = rendered["cv"]
    cv["headline"] = variant_meta.get("headline", cv.get("headline"))

    sections = cv.get("sections", {})
    filtered_sections = {}
    for section_name, entries in sections.items():
        if not isinstance(entries, list):
            filtered_sections[section_name] = entries
            continue

        selected = [strip_helper_fields(item) for item in entries if include_entry(item, variant)]
        if selected:
            filtered_sections[section_name] = selected

    cv["sections"] = filtered_sections
    cv["photo"] = resolve_relative_asset(cv.get("photo", ""), OUTPUT_FILES[variant].parent)
    return {"cv": cv}


def write_variant(variant: str, payload: dict) -> None:
    path = OUTPUT_FILES[variant]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Generated from cv/master/jesus_erro_cv_master.yaml for variant: {variant}\n")
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def main() -> int:
    args = parse_args()
    master = load_master()
    variants = args.variants or list(VARIANTS)
    for variant in variants:
        write_variant(variant, build_variant(master, variant))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
