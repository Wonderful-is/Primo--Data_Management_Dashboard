"""
Shared constants and transformation helpers used by all dashboard routers.
This mirrors the logic that previously lived inside app.py / review_app.py /
daily_missing_app.py, but operates on data pulled from Postgres (Neon)
instead of local CSV files.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# FORM RELABELLING
# ---------------------------------------------------------------------------

FORM_RELABEL = {
    "formulaire_quotidien_daily_form": "Daily Form",
    "formulaire_rsum_des_tests_cliniques_des_pathognes": "Maternal Clinical Pathogen",
    "outcome_form": "Outcome Form",
    "formulaire_de_grossesse_et_de_suivi_pregnancy_and": "Prenatal Form",
    "formulaire_de_rsultat_de_grossesse_pregnancy_outco": "Postpartum Form",
    "formulaire_de_registration_nonatal_neonatal_regist": "Neonatal Registration",
    "formulaire_de_suivi_nonatal_neonatal_follow_up_for": "Neonatal Follow-up",
}

CP_VARS = [
    "clinical_pathogen_samples",
    "collection_date_1",
    "biospecimen_type_1",
    "lab_test_method_1",
    "ltm_result_1",
    "pathogen_tested_detected_1",
    "ct_value_1",
    "specify_reason_for_no",
]

# ---------------------------------------------------------------------------
# EVENT ORDERS / LABELS
# ---------------------------------------------------------------------------

DAILY_EVENT_ORDER = [
    "baseline_arm_1",
    "day_4_arm_1",
    "day_8_arm_1",
    "day_14_arm_1",
    "day_21_arm_1",
    "day_60_arm_1",
    "admission_to_icu_o_arm_1",
    "day_180_arm_1",
]

PRENATAL_EVENT_ORDER = [
    "prenatal_1_arm_1",
    "prenatal_2_arm_1",
    "prenatal_3_arm_1",
    "prenatal_4_arm_1",
]

NEONATAL_EVENT_ORDER = [
    "neonatal_1_m0_arm_2",
    "neonatal_2_m1_arm_2",
    "neonatal_3_m2_arm_2",
    "neonatal_4_m3_arm_2",
    "neonatal_5_m4_arm_2",
    "neonatal_6_m5_arm_2",
    "neonatal_7_m6_arm_2",
    "neonatal_8_m7_arm_2",
    "neonatal_9_m8_arm_2",
    "neonatal_10_m9_arm_2",
    "neonatal_11_m10_arm_2",
    "neonatal_12_m11_arm_2",
]

EVENT_LABELS = {
    "baseline_arm_1": "Day 1 / Baseline",
    "day_4_arm_1": "Day 4",
    "day_8_arm_1": "Day 8",
    "day_14_arm_1": "Day 14",
    "day_21_arm_1": "Day 21",
    "day_60_arm_1": "Day 60",
    "admission_to_icu_o_arm_1": "ICU/CC",
    "day_180_arm_1": "Day 180",
    "prenatal_1_arm_1": "P1",
    "prenatal_2_arm_1": "P2",
    "prenatal_3_arm_1": "P3",
    "prenatal_4_arm_1": "P4",
    "neonatal_1_m0_arm_2": "M0",
    "neonatal_2_m1_arm_2": "M1",
    "neonatal_3_m2_arm_2": "M2",
    "neonatal_4_m3_arm_2": "M3",
    "neonatal_5_m4_arm_2": "M4",
    "neonatal_6_m5_arm_2": "M5",
    "neonatal_7_m6_arm_2": "M6",
    "neonatal_8_m7_arm_2": "M7",
    "neonatal_9_m8_arm_2": "M8",
    "neonatal_10_m9_arm_2": "M9",
    "neonatal_11_m10_arm_2": "M10",
    "neonatal_12_m11_arm_2": "M11",
    "clinical_pathogen_event_arm_1": "Clinical Pathogen Event",
    "outcome_arm_1": "Outcome",
    "postpartum_arm_1": "Postpartum",
}

# ---------------------------------------------------------------------------
# FORM / PARTICIPANT TYPE GROUPS (used by review dashboard)
# ---------------------------------------------------------------------------

MOTHER_FORMS = [
    "Presentation Form",
    "Daily Form",
    "Maternal Clinical Pathogen",
    "Outcome Form",
    "Prenatal Form",
    "Postpartum Form",
]

BABY_FORMS = [
    "Neonatal Registration",
    "Neonatal Follow-up",
    "Neonatal Clinical Pathogen",
]

FORM_ALLOWED_PARTICIPANT_TYPE = {
    **{form: "Mother" for form in MOTHER_FORMS},
    **{form: "Baby" for form in BABY_FORMS},
}

ARM_ALLOWED_FORMS = {
    "Femme": MOTHER_FORMS,
    "Bebe": BABY_FORMS,
    "All": MOTHER_FORMS + BABY_FORMS,
}

FORM_EVENT_MAP = {
    "Presentation Form": ["baseline_arm_1"],
    "Daily Form": DAILY_EVENT_ORDER,
    "Maternal Clinical Pathogen": ["clinical_pathogen_event_arm_1"],
    "Outcome Form": ["outcome_arm_1"],
    "Prenatal Form": PRENATAL_EVENT_ORDER,
    "Postpartum Form": ["postpartum_arm_1"],
    "Neonatal Registration": ["neonatal_1_m0_arm_2"],
    "Neonatal Follow-up": NEONATAL_EVENT_ORDER,
    "Neonatal Clinical Pathogen": NEONATAL_EVENT_ORDER,
}

BABY_LINK_OPTIONS = [
    "All",
    "Mother with baby",
    "Mother without baby",
    "Baby linked to mother",
    "Baby without mother link",
]

# ---------------------------------------------------------------------------
# DAILY MISSING-VISIT REVIEW
# ---------------------------------------------------------------------------

DAILY_VISITS = {
    "Day 1": ("baseline_arm_1", 0),
    "Day 4": ("day_4_arm_1", 4),
    "Day 8": ("day_8_arm_1", 8),
    "Day 14": ("day_14_arm_1", 14),
    "Day 21": ("day_21_arm_1", 21),
    "Day 60": ("day_60_arm_1", 60),
    "Day 180": ("day_180_arm_1", 180),
}

VISIT_LABELS = list(DAILY_VISITS.keys())

DAILY_FORM = "formulaire_quotidien_daily_form"


# ---------------------------------------------------------------------------
# CORE PREP: add site / form / form_dashboard columns to the master dataframe
# ---------------------------------------------------------------------------

def prepare_master(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    data["site"] = data["family_id"].astype(str).str.extract(r"^([A-Z]+)")
    data["form"] = data["redcap_repeat_instrument"].fillna("Event / Non-repeating")
    data["form_dashboard"] = data["form"].replace(FORM_RELABEL)

    presentation_mask = (
        (data["participant_type"] == "Mother")
        & (data["redcap_event_name"] == "baseline_arm_1")
        & (data["redcap_repeat_instrument"].isna())
    )
    data.loc[presentation_mask, "form_dashboard"] = "Presentation Form"

    cp_vars_present = [c for c in CP_VARS if c in data.columns]

    if cp_vars_present:
        neonatal_cp_mask = (
            (data["participant_type"] == "Baby")
            & (data["redcap_repeat_instrument"].isna())
            & (data[cp_vars_present].notna().any(axis=1))
        )
        data.loc[neonatal_cp_mask, "form_dashboard"] = "Neonatal Clinical Pathogen"

    return data


def parse_date_column(df: pd.DataFrame, col: str):
    if col in df.columns:
        return pd.to_datetime(df[col], errors="coerce", dayfirst=False)
    return pd.Series(pd.NaT, index=df.index)


# ---------------------------------------------------------------------------
# REVIEW BASE: participant roster + mother/baby linkage (review_app.py)
# ---------------------------------------------------------------------------

def build_participant_base(data: pd.DataFrame) -> pd.DataFrame:
    participant_base = (
        data[["participant_id", "family_id", "site", "participant_type", "study_arm"]]
        .drop_duplicates()
        .dropna(subset=["participant_id"])
        .copy()
    )

    mother_ids = set(
        participant_base.loc[
            participant_base["participant_type"] == "Mother", "participant_id"
        ]
    )

    baby_family_ids = set(
        participant_base.loc[
            participant_base["participant_type"] == "Baby", "family_id"
        ]
    )

    participant_base["baby_link_status"] = "Not applicable"

    participant_base.loc[
        participant_base["participant_type"] == "Mother", "baby_link_status"
    ] = participant_base.loc[
        participant_base["participant_type"] == "Mother", "participant_id"
    ].apply(lambda x: "Mother with baby" if x in baby_family_ids else "Mother without baby")

    participant_base.loc[
        participant_base["participant_type"] == "Baby", "baby_link_status"
    ] = participant_base.loc[
        participant_base["participant_type"] == "Baby", "family_id"
    ].apply(lambda x: "Baby linked to mother" if x in mother_ids else "Baby without mother link")

    return participant_base


# ---------------------------------------------------------------------------
# DATE-AWARE DAILY MISSING REVIEW BASE (daily_missing_app.py)
# ---------------------------------------------------------------------------

def build_daily_review_base(data: pd.DataFrame, roster: pd.DataFrame) -> pd.DataFrame:
    roster = roster.copy()
    roster["site"] = roster["family_id"].astype(str).str.extract(r"^([A-Z]+)")

    mothers = roster[roster["participant_type"] == "Mother"].copy()
    mothers = mothers[
        ["participant_id", "family_id", "site", "participant_type", "study_arm"]
        if "study_arm" in mothers.columns
        else ["participant_id", "family_id", "site", "participant_type"]
    ].drop_duplicates()

    if "study_arm" not in mothers.columns:
        mothers["study_arm"] = None

    presentation = data[
        (data["participant_type"] == "Mother")
        & (data["redcap_event_name"] == "baseline_arm_1")
        & (data["redcap_repeat_instrument"].isna())
    ].copy()

    presentation["date_consent_recruitment_parsed"] = parse_date_column(
        presentation, "date_consent_recruitment"
    )

    presentation_dates = (
        presentation[["participant_id", "date_consent_recruitment_parsed"]]
        .dropna(subset=["participant_id"])
        .drop_duplicates("participant_id")
    )

    postpartum = data[data["redcap_event_name"] == "postpartum_arm_1"].copy()
    postpartum["has_postpartum_form"] = True

    possible_delivery_date_cols = [
        "date_dmy",
        "date_accouchement",
        "date_daccouchement",
        "delivery_date",
        "post_partum_yes",
    ]

    existing_delivery_cols = [c for c in possible_delivery_date_cols if c in postpartum.columns]

    postpartum["delivery_date"] = pd.NaT
    for col in existing_delivery_cols:
        parsed = pd.to_datetime(postpartum[col], errors="coerce", dayfirst=False)
        postpartum["delivery_date"] = postpartum["delivery_date"].fillna(parsed)

    postpartum_info = (
        postpartum[["participant_id", "delivery_date", "has_postpartum_form"]]
        .dropna(subset=["participant_id"])
        .sort_values("delivery_date")
        .drop_duplicates("participant_id", keep="first")
    )

    neonatal_registration = data[data["redcap_event_name"] == "neonatal_1_m0_arm_2"].copy()
    neonatal_registration["infant_dob_parsed"] = parse_date_column(
        neonatal_registration, "infant_dob"
    )

    baby_info = (
        neonatal_registration[["family_id", "participant_id", "infant_dob_parsed"]]
        .rename(columns={"participant_id": "baby_id"})
        .dropna(subset=["family_id"])
        .sort_values(["family_id", "infant_dob_parsed"], ascending=[True, False], na_position="last")
        .drop_duplicates("family_id", keep="first")
    )
    baby_info["has_baby"] = True

    review_base = mothers.merge(presentation_dates, on="participant_id", how="left")
    review_base = review_base.merge(postpartum_info, on="participant_id", how="left")
    review_base = review_base.merge(
        baby_info[["family_id", "baby_id", "infant_dob_parsed", "has_baby"]],
        on="family_id",
        how="left",
    )

    review_base["has_postpartum_form"] = review_base["has_postpartum_form"].fillna(False)
    review_base["has_baby"] = review_base["has_baby"].fillna(False)

    review_base["reference_delivery_date"] = review_base["delivery_date"].fillna(
        review_base["infant_dob_parsed"]
    )

    daily_completed = (
        data[data["redcap_repeat_instrument"] == DAILY_FORM][["participant_id", "redcap_event_name"]]
        .dropna()
        .drop_duplicates()
    )

    for visit_label, (event_name, offset_days) in DAILY_VISITS.items():
        completed_ids = set(
            daily_completed.loc[daily_completed["redcap_event_name"] == event_name, "participant_id"]
        )

        expected_date_col = f"{visit_label}_expected_date"
        status_col = f"{visit_label}_status"

        review_base[expected_date_col] = review_base["date_consent_recruitment_parsed"] + pd.to_timedelta(
            offset_days, unit="D"
        )

        def classify_visit(row, expected_date_col=expected_date_col, completed_ids=completed_ids):
            expected_date = row[expected_date_col]
            delivery_date = row["reference_delivery_date"]
            participant_id = row["participant_id"]

            if pd.isna(expected_date):
                return "Unknown enrollment date"

            if pd.notna(delivery_date) and expected_date > delivery_date:
                return "Not expected after delivery"

            if participant_id in completed_ids:
                return "Completed"

            return "Missing"

        review_base[status_col] = review_base.apply(classify_visit, axis=1)

    return review_base


def df_to_records(df: pd.DataFrame):
    """Convert a dataframe to JSON-safe list-of-dicts (handles NaT/NaN/Timestamps)."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    out = out.where(pd.notna(out), None)
    return out.to_dict("records")
