from services.alma.analytics import AlmaAnalytics
from os import path

REPORTS_DICTIONARY = {
    "circulation_stats": {
        "path": "/shared/Boston%20University/Reports/jwa/NumberOfLoansPast7days",
        "output": "circ_stats.tsv"
    },
    "openurl_article": {
        "path": "/shared/Boston%20University/Reports/jwa/Top%20ten%20article%20title%20accesses%20via%20OpenURL",
        "output": "open_url_article_stats.tsv"
    },
    "openurl_journal": {
        "path": "/shared/Boston%20University/Reports/jwa/Top%20ten%20title%20accesses%20via%20OpenURL%20requests",
        "output": "open_url_title_stats.tsv"
    },
    "openurl_request": {
        "path": "/shared/Boston%20University/Reports/jwa/Top%20ten%20title%20accesses%20via%20OpenURL%20requests",
        "output": "open_url_request_stats.tsv"
    }
}


def run_weekly_circulation_statistics(upload_directory):
    alma_analytics_svc = AlmaAnalytics(use_production=True)

    for report in REPORTS_DICTIONARY:
        report_response_data = alma_analytics_svc.prepare_df_from_report_path(REPORTS_DICTIONARY[report]["path"])
        output_path = path.join(upload_directory, REPORTS_DICTIONARY[report]["output"])
        report_response_data.to_csv(output_path, sep='\t')

