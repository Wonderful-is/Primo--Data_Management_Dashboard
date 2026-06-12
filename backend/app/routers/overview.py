from typing import List, Optional

from fastapi import APIRouter, Query

from .. import transforms as t
from ..data_loader import get_cache

router = APIRouter(prefix="/api/overview", tags=["overview"])


def _split(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value == "":
        return None
    return value.split(",")


@router.get("/filters")
def get_filters():
    cache = get_cache()
    data = cache["data"]
    query_log = cache["query_log"]

    return {
        "sites": sorted(data["site"].dropna().unique().tolist()),
        "forms": sorted(data["form_dashboard"].dropna().unique().tolist()),
        "participant_types": sorted(data["participant_type"].dropna().unique().tolist()),
        "statuses": sorted(query_log["Status"].dropna().unique().tolist()) if "Status" in query_log.columns else [],
    }


@router.get("/data")
def get_overview_data(
    sites: Optional[str] = Query(default=None, description="Comma-separated site codes"),
    forms: Optional[str] = Query(default=None, description="Comma-separated form_dashboard values"),
    ptype: Optional[str] = Query(default="All", description="Mother / Baby / All"),
    status: Optional[str] = Query(default=None, description="Comma-separated query statuses"),
):
    cache = get_cache()
    data = cache["data"]
    query_log = cache["query_log"]

    site_list = _split(sites) or sorted(data["site"].dropna().unique().tolist())
    form_list = _split(forms) or sorted(data["form_dashboard"].dropna().unique().tolist())
    status_list = _split(status) or (
        sorted(query_log["Status"].dropna().unique().tolist()) if "Status" in query_log.columns else []
    )

    dff = data[data["site"].isin(site_list) & data["form_dashboard"].isin(form_list)].copy()

    if ptype and ptype != "All":
        dff = dff[dff["participant_type"] == ptype]

    if "Status" in query_log.columns:
        qff = query_log[query_log["Status"].isin(status_list)].copy()
    else:
        qff = query_log.copy()

    # ---- KPIs ----
    total_records = int(len(dff))
    total_participants = int(dff["participant_id"].nunique())
    mothers = int(dff.loc[dff["participant_type"] == "Mother", "participant_id"].nunique())
    babies = int(dff.loc[dff["participant_type"] == "Baby", "participant_id"].nunique())
    n_sites = int(dff["site"].nunique())
    open_queries = int(qff["Status"].eq("Open").sum()) if "Status" in qff.columns else 0

    kpis = {
        "total_records": total_records,
        "participants": total_participants,
        "mothers": mothers,
        "babies": babies,
        "sites": n_sites,
        "open_queries": open_queries,
    }

    # ---- Records by participant type (pie) ----
    participant_chart = (
        dff.drop_duplicates("participant_id")
        .groupby("participant_type")
        .size()
        .reset_index(name="value")
        .rename(columns={"participant_type": "name"})
    )

    # ---- Participants by site (bar) ----
    site_chart = (
        dff.drop_duplicates("participant_id")
        .groupby("site")
        .size()
        .reset_index(name="Participants")
        .rename(columns={"site": "name"})
    )

    # ---- Form inventory (bar) ----
    form_chart = (
        dff.groupby("form_dashboard")
        .size()
        .reset_index(name="Records")
        .sort_values("Records")
        .rename(columns={"form_dashboard": "name"})
    )

    # ---- Maternal daily coverage (line) ----
    daily_data = dff[dff["redcap_repeat_instrument"] == "formulaire_quotidien_daily_form"]
    daily_cov = (
        daily_data.groupby("redcap_event_name")["participant_id"]
        .nunique()
        .reindex(t.DAILY_EVENT_ORDER)
        .dropna()
        .reset_index()
    )
    daily_cov.columns = ["event", "Participants"]
    daily_cov["name"] = daily_cov["event"].map(t.EVENT_LABELS)
    daily_chart = daily_cov[["name", "Participants"]]

    # ---- Prenatal follow-up coverage (line) ----
    prenatal_data = dff[dff["form_dashboard"] == "Prenatal Form"]
    prenatal_cov = (
        prenatal_data.groupby("redcap_event_name")["participant_id"]
        .nunique()
        .reindex(t.PRENATAL_EVENT_ORDER)
        .dropna()
        .reset_index()
    )
    prenatal_cov.columns = ["event", "Participants"]
    prenatal_cov["name"] = prenatal_cov["event"].map(t.EVENT_LABELS)
    prenatal_chart = prenatal_cov[["name", "Participants"]]

    # ---- Neonatal follow-up coverage (line) ----
    neonatal_data = dff[
        dff["redcap_repeat_instrument"] == "formulaire_de_suivi_nonatal_neonatal_follow_up_for"
    ]
    neo_cov = (
        neonatal_data.groupby("redcap_event_name")["participant_id"]
        .nunique()
        .reindex(t.NEONATAL_EVENT_ORDER)
        .dropna()
        .reset_index()
    )
    neo_cov.columns = ["event", "Babies"]
    neo_cov["name"] = neo_cov["event"].map(t.EVENT_LABELS)
    neonatal_chart = neo_cov[["name", "Babies"]]

    # ---- Neonatal clinical pathogen coverage (line) ----
    neonatal_cp_data = dff[dff["form_dashboard"] == "Neonatal Clinical Pathogen"]
    neonatal_cp_cov = (
        neonatal_cp_data.groupby("redcap_event_name")["participant_id"]
        .nunique()
        .reindex(t.NEONATAL_EVENT_ORDER)
        .dropna()
        .reset_index()
    )
    neonatal_cp_cov.columns = ["event", "Babies"]
    neonatal_cp_cov["name"] = neonatal_cp_cov["event"].map(t.EVENT_LABELS)
    neonatal_cp_chart = neonatal_cp_cov[["name", "Babies"]]

    # ---- Query status (bar) ----
    if "Status" in qff.columns:
        query_chart = qff.groupby("Status").size().reset_index(name="Count").rename(columns={"Status": "name"})
    else:
        query_chart = qff.iloc[0:0]

    return {
        "kpis": kpis,
        "charts": {
            "participant_type": t.df_to_records(participant_chart),
            "by_site": t.df_to_records(site_chart),
            "by_form": t.df_to_records(form_chart),
            "daily_coverage": t.df_to_records(daily_chart),
            "prenatal_coverage": t.df_to_records(prenatal_chart),
            "neonatal_coverage": t.df_to_records(neonatal_chart),
            "neonatal_cp_coverage": t.df_to_records(neonatal_cp_chart),
            "query_status": t.df_to_records(query_chart),
        },
        "query_log": {
            "columns": list(qff.columns),
            "rows": t.df_to_records(qff),
        },
    }
