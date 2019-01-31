from services import OUTPUT_DIRECTORY, construct_log_message
from services.analytics import AlmaAnalytics, PrimoAnalytics
from os import makedirs
from os.path import abspath, join, basename

ALMA_REPORTS = {
    "circulation_stats": {
        "path": "/shared/Boston University/Reports/jwa/NumberOfLoansPast7days",
        "output": "circ_stats.tsv"
    },
    "openurl_article": {
        "path": "/shared/Boston University/Reports/jwa/Top ten article title accesses via OpenURL",
        "output": "open_url_article_stats.tsv"
    },
    "openurl_journal": {
        "path": "/shared/Boston University/Reports/jwa/Top ten title accesses via OpenURL requests",
        "output": "open_url_title_stats.tsv"
    },
    "openurl_request": {
        "path": "/shared/Boston University/Reports/jwa/Top ten title accesses via OpenURL requests",
        "output": "open_url_request_stats.tsv"
    }
}

PRIMO_API_TEST_REPORTS = {
    "api_nui": {
        "path": "/shared/Primo Boston University Libraries/Reports/DataStudio/nuiFacetsForGDS",
        "output": "nui_actions_for_GDS.tsv"
    },
    "api_actions": {
        "path": "/shared/Primo Boston University Libraries/Reports/API_TestsAPI/Test-ActionsForGDS",
        "output": "actions_for_GDS.tsv"
    },
    "api_facets": {
        "path": "/shared/Primo Boston University Libraries/Reports/API_Tests/APITest-FacetsForGDS",
        "output": "facets_for_GDS.tsv"
    },
    "api_tabs": {
        "path": "/shared/Primo Boston University Libraries/Reports/API_Tests/APITest-Tabs",
        "output": "tabs_for_GDS.tsv"
    }
}

# name of the current script, for use in logging
SCRIPT_NAME = basename(__file__)


def run_reports_from_dictionary(service, reports_dict, project_id="jwasys/bu-lib-stats", output_dir=OUTPUT_DIRECTORY, upload_upon_completion=False):
    try:
        makedirs(output_dir)
    except FileExistsError:
        pass  # directory already existed

    for report in reports_dict:
        input_path = reports_dict[report]["path"]
        output_filename = reports_dict[report]["output"]
        print(construct_log_message(SCRIPT_NAME, "running report for output: '" + output_filename + "'"))

        try:
            report_response_data = service.prepare_df_from_report_path(input_path)
            output_report_path = abspath(join(output_dir, output_filename))
            report_response_data.to_csv(output_report_path, sep='\t')

            if upload_upon_completion:
                service.upload_to_dw(output_report_path, project_id)
        except ValueError as error:
            print(construct_log_message(SCRIPT_NAME, "Error running report : '" + input_path + "'\n-> {}\n".format(error), level="WARN"))


def run_weekly_circulation_statistics():
    alma_analytics_svc = AlmaAnalytics(use_production=True)
    output_directory = join(OUTPUT_DIRECTORY, "alma/")
    run_reports_from_dictionary(alma_analytics_svc, ALMA_REPORTS, output_dir=output_directory)


def run_monthly_primo_api_tests():
    primo_analytics_svc = PrimoAnalytics(use_production=True)
    output_directory = join(OUTPUT_DIRECTORY, "primo/api_tests/")
    run_reports_from_dictionary(primo_analytics_svc, PRIMO_API_TEST_REPORTS, output_dir=output_directory)


if __name__ == "__main__":
    run_weekly_circulation_statistics()
    run_monthly_primo_api_tests()
