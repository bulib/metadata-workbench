"""
## Code to gather data from Alma Analytics and Upload to Data.World
## CREATED: jwammerman (jwacooks) 2017-10-27
## EDITED: aidans (atla5) 2019-01
"""
# import datadotworld as dw
from pandas import DataFrame
from time import sleep
from os.path import join
from xml.etree import ElementTree as ET

from services import Service, OUTPUT_DIRECTORY, get_api_key
from services.alma import CONTENT_TYPE_XML

# assorted magical
DEFAULT_LIMIT = 1000
NS = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
KEY = get_api_key("alma", "analytics", "production")

# report information
SAMPLE_DW_UPLOAD_PROJECT = "jwasys/bu-lib-stats"
SAMPLE_REPORT_PATH_IN = "/shared/Boston%20University/Reports/jwa/NumberOfLoansPast7days"
SAMPLE_REPORT_PATH_OUT  = join(OUTPUT_DIRECTORY, "circ_stats.tsv")


def is_report_finished(report):
    return report.find('*/IsFinished').text != 'false'


class AlmaAnalytics(Service):

    def __init__(self, use_production=False, logging=True):
        super(AlmaAnalytics, self).__init__(use_production, logging)  # properly subclass from Service
        self.base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
        self.api_key = KEY

    def prepare_df_from_report_path(self, reportPath, secondsBetweenRequests=1):
        self.log_message("requesting report for the first time by the reportPath: '" + reportPath + "'...")
        report = self.request_analytics_report_by_path(reportPath)

        # if the report isn't finished, use its 'ResumptionToken' to keep re-asking about it until it is
        while not is_report_finished(report):
            sleep(secondsBetweenRequests)
            resumption_token = report.find('*/ResumptionToken').text
            self.log_message("re-requesting report via the ResumptionToken: '" + resumption_token + "'...")
            report = self.request_analytics_report_by_token(resumption_token)

        # process and convert the data into a pandas 'DataFrame' and (optionally) save to disk
        output_data_frame = self.process_completed_report_into_df(report)
        return output_data_frame

    def request_analytics_report_by_path(self, pathToReport, limit=DEFAULT_LIMIT):
        api_path = '/analytics/reports'
        query_params = {"limit": limit, "path": pathToReport}
        response = self.make_request(api_path, queryParams=query_params, headers=CONTENT_TYPE_XML)
        report = ET.fromstring(response)
        return report

    def request_analytics_report_by_token(self, resumptionToken):
        api_path = '/analytics/reports'
        query_params = {"token": resumptionToken}
        response = self.make_request(api_path, queryParams=query_params, headers=CONTENT_TYPE_XML)
        report = ET.fromstring(response)
        return report

    def process_completed_report_into_df(self, report):
        results = report.find('*/ResultXml')
        rows = results.findall('*/ns0:Row', NS)
        self.log_message("numRows: " + str(len(rows)))

        # convert information into Pandas DataFrame
        df = DataFrame()
        row_dict = {}
        for row in rows:
            for col in list(row):  # row.getchildren()
                row_dict[col.tag[-7:]] = col.text
            row_dict
            df = df.append(row_dict, ignore_index=True)

        columns = []
        resultXml = report.findall('./*/ResultXml')[0]
        rowset = resultXml.find('./{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
        sequence = rowset.findall('./*/*/*/*')
        for el in sequence:
            columns.append(el.attrib['{urn:saw-sql}columnHeading'].replace(' REPORT_SUM(', '').replace(' Name)', ''))

        print('total: ', df.shape[0])
        df.columns = columns
        df.head()
        return df

    def upload_to_dw(self, filepath, project_name):
        dw = "placeholder"  # TODO: resolve 'datadotworld' import error
        api_client = dw.api_client()
        # api_client.create_dataset('jwasys', title='bu-lib-stats', visibility='PRIVATE', license='Public Domain')
        api_client.upload_files(project_name, filepath)


if __name__ == "__main__":
    alma_analytics_svc = AlmaAnalytics(use_production=True)
    report_response_data = alma_analytics_svc.prepare_df_from_report_path(SAMPLE_REPORT_PATH_IN)
    report_response_data.to_csv(SAMPLE_REPORT_PATH_OUT, sep='\t')
