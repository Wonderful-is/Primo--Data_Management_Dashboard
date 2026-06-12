from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Query

from .. import transforms as t
from ..data_loader import get_cache

router = APIRouter(prefix="/api/daily-missing", tags=["daily-missing"])


def _split(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value == "":
        return None
    return value.split(",")


@router.get("/filters")
def get_filters():
    cache = get_cache()
    review_base = cache["daily_review_base"]

    return {
        "site_options": sorted(review_base["site"].dropna().unique().tolist()),
        "visit_labels": t.VISIT_LABELS,
        "delivery_filter_options": [
            "All",
            "Has postpartum",
            "No postpartum",
            "Has baby",
            "No baby",
        ],
    }


@router.get("/data")
def get_daily_missing_data(
    sites: Optional[str] = Query(default=None, description="Comma-separated site codes"),
    include_visits: Optional[str] = Query(
        default="Day 8,Day 14,Day 21,Day 60,Day 180",
        description="Comma-separated visit labels - participant must be Missing ALL of these",
    ),
    exclude_visits: Optional[str] = Query(
        default=None,
        description="Comma-separated visit labels - exclude participants Missing ALL of these",
    ),
    delivery_filter: str = Query(default="All"),
):
    cache = get_cache()
    review_base = cache["daily_review_base"]

    site_list = _split(sites) or sorted(review_base["site"].dropna().unique().tolist())
    review = review_base[review_base["site"].isin(site_list)].copy()

    if delivery_filter == "Has postpartum":
        review = review[review["has_postpartum_form"] == True]  # noqa: E712
    elif delivery_filter == "No postpartum":
        review = review[review["has_postpartum_form"] == False]  # noqa: E712
    elif delivery_filter == "Has baby":
        review = review[review["has_baby"] == True]  # noqa: E712
    elif delivery_filter == "No baby":
        review = review[review["has_baby"] == False]  # noqa: E712

    include_list = _split(include_visits) or []
    exclude_list = _split(exclude_visits) or []
    exclude_list = [v for v in exclude_list if v not in include_list]

    # ---- summary table ----
    summary_rows = []
    for visit in t.VISIT_LABELS:
        status_col = f"{visit}_status"
        if status_col in review.columns:
            summary_rows.append(
                {
                    "Visit": visit,
                    "Missing Mothers": int((review[status_col] == "Missing").sum()),
                    "Completed Mothers": int((review[status_col] == "Completed").sum()),
                    "Not Expected After Delivery": int(
                        (review[status_col] == "Not expected after delivery").sum()
                    ),
                    "Unknown Enrollment Date": int(
                        (review[status_col] == "Unknown enrollment date").sum()
                    ),
                }
            )

    missing_summary_df = pd.DataFrame(summary_rows)

    # ---- include / exclude masks ----
    if include_list:
        include_status_cols = [f"{v}_status" for v in include_list]
        include_mask = review[include_status_cols].eq("Missing").all(axis=1)
    else:
        include_mask = pd.Series(True, index=review.index)

    if exclude_list:
        exclude_status_cols = [f"{v}_status" for v in exclude_list]
        exclude_mask = review[exclude_status_cols].eq("Missing").all(axis=1)
    else:
        exclude_mask = pd.Series(False, index=review.index)

    result = review[include_mask & ~exclude_mask].copy()

    display_cols = [
        "participant_id",
        "family_id",
        "site",
        "study_arm",
        "date_consent_recruitment_parsed",
        "has_postpartum_form",
        "delivery_date",
        "has_baby",
        "baby_id",
        "infant_dob_parsed",
        "reference_delivery_date",
    ]

    for visit in t.VISIT_LABELS:
        display_cols.append(f"{visit}_expected_date")
        display_cols.append(f"{visit}_status")

    display_cols = [c for c in display_cols if c in result.columns]
    result = result[display_cols].sort_values(["site", "participant_id"])

    date_cols = [c for c in result.columns if "date" in c.lower()]
    for col in date_cols:
        result[col] = pd.to_datetime(result[col], errors="coerce").dt.strftime("%Y-%m-%d")
        result[col] = result[col].fillna("")

    include_text = ", ".join(include_list) if include_list else "None"
    exclude_text = ", ".join(exclude_list) if exclude_list else "None"

    note = (
        f"Showing mothers missing ALL selected expected visits: {include_text}. "
        f"Excluding mothers missing ALL of: {exclude_text}. "
        f"A visit is counted as Missing only if its expected date is not after the "
        f"delivery date or infant DOB."
    )

    return {
        "summary_table": {
            "columns": list(missing_summary_df.columns),
            "rows": t.df_to_records(missing_summary_df),
        },
        "missing_table": {
            "columns": list(result.columns),
            "rows": t.df_to_records(result),
        },
        "kpis": {
            "eligible": int(len(review)),
            "matched": int(len(result)),
            "include_pattern": include_text,
            "exclude_pattern": exclude_text,
        },
        "note": note,
    }
