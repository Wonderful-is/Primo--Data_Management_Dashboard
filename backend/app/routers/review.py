from typing import List, Optional

from fastapi import APIRouter, Query

from .. import transforms as t
from ..data_loader import get_cache

router = APIRouter(prefix="/api/review", tags=["review"])


def _split(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value == "":
        return None
    return value.split(",")


@router.get("/filters")
def get_filters():
    cache = get_cache()
    participant_base = cache["participant_base"]

    site_options = sorted(participant_base["site"].dropna().unique().tolist())
    arm_options = ["All"] + sorted(participant_base["study_arm"].dropna().unique().tolist())
    ptype_options = ["All"] + sorted(participant_base["participant_type"].dropna().unique().tolist())

    return {
        "site_options": site_options,
        "arm_options": arm_options,
        "ptype_options": ptype_options,
        "baby_link_options": t.BABY_LINK_OPTIONS,
        "arm_allowed_forms": t.ARM_ALLOWED_FORMS,
        "form_event_map": t.FORM_EVENT_MAP,
        "event_labels": t.EVENT_LABELS,
        "form_allowed_participant_type": t.FORM_ALLOWED_PARTICIPANT_TYPE,
    }


@router.get("/data")
def get_review_data(
    sites: Optional[str] = Query(default=None, description="Comma-separated site codes"),
    arm: str = Query(default="All"),
    ptype: str = Query(default="All"),
    form: Optional[str] = Query(default=None, description="Form to review (form_dashboard value)"),
    event: Optional[str] = Query(default=None, description="redcap_event_name to review"),
    completion: str = Query(default="Missing", description="All | Completed | Missing"),
    baby_link: str = Query(default="All"),
):
    cache = get_cache()
    data = cache["data"]
    participant_base = cache["participant_base"]

    site_list = _split(sites) or sorted(participant_base["site"].dropna().unique().tolist())

    if form is None or event is None or form not in t.FORM_ALLOWED_PARTICIPANT_TYPE:
        return {
            "rows": [],
            "columns": [],
            "kpis": {"total": 0, "completed": 0, "missing": 0, "completion_pct": 0},
            "eligibility_note": "Please select a form and visit/event.",
        }

    required_type = t.FORM_ALLOWED_PARTICIPANT_TYPE[form]

    review = participant_base[participant_base["site"].isin(site_list)].copy()

    if arm != "All":
        review = review[review["study_arm"] == arm]

    if ptype != "All":
        review = review[review["participant_type"] == ptype]

    if baby_link != "All":
        review = review[review["baby_link_status"] == baby_link]

    review = review[review["participant_type"] == required_type]

    completed_ids = (
        data[(data["form_dashboard"] == form) & (data["redcap_event_name"] == event)]["participant_id"]
        .dropna()
        .unique()
    )

    review["form_reviewed"] = form
    review["visit_reviewed"] = t.EVENT_LABELS.get(event, event)
    review["eligible_for_form"] = "Yes"
    review["form_status"] = review["participant_id"].isin(completed_ids)
    review["form_status"] = review["form_status"].map({True: "Completed", False: "Missing"})

    total_n = int(len(review))
    completed_n = int((review["form_status"] == "Completed").sum())
    missing_n = int((review["form_status"] == "Missing").sum())
    completion_pct = round((completed_n / total_n) * 100, 1) if total_n > 0 else 0

    if completion != "All":
        review = review[review["form_status"] == completion]

    review = review[
        [
            "participant_id",
            "family_id",
            "site",
            "study_arm",
            "participant_type",
            "baby_link_status",
            "form_reviewed",
            "visit_reviewed",
            "eligible_for_form",
            "form_status",
        ]
    ].sort_values(["form_status", "site", "participant_id"])

    eligibility_note = (
        f"{form} at {t.EVENT_LABELS.get(event, event)} is expected only for {required_type} "
        f"participants. Participants outside this group are excluded from missing counts."
    )

    return {
        "rows": t.df_to_records(review),
        "columns": list(review.columns),
        "kpis": {
            "total": total_n,
            "completed": completed_n,
            "missing": missing_n,
            "completion_pct": completion_pct,
        },
        "eligibility_note": eligibility_note,
    }
