from services import OUTPUT_DIRECTORY, construct_log_message
from services.alma.analytics import AlmaAnalytics
from os.path import abspath, join, basename

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

# name of the current script, for use in logging
SCRIPT_NAME = basename(__file__)


def run_weekly_circulation_statistics(output_dir=OUTPUT_DIRECTORY, upload_to_dw=False):
    alma_analytics_svc = AlmaAnalytics(use_production=True)

    for report in REPORTS_DICTIONARY:
        input_path = REPORTS_DICTIONARY[report]["path"]
        print(construct_log_message(SCRIPT_NAME, "running report for output: " + input_path))

        try:
            report_response_data = alma_analytics_svc.prepare_df_from_report_path(input_path)

            output_report_path = abspath(join(output_dir, REPORTS_DICTIONARY[report]["output"]))
            report_response_data.to_csv(output_report_path, sep='\t')

            if upload_to_dw:
                alma_analytics_svc.upload_to_dw(output_report_path, "jwasys/bu-lib-stats")
        except ValueError as error:
            print(construct_log_message(SCRIPT_NAME, "Error running report : '" + input_path + "'\n-> {}\n".format(error), level="WARN"))


if __name__ == "__main__":
    run_weekly_circulation_statistics(OUTPUT_DIRECTORY)
