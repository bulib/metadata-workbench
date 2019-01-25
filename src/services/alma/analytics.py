"""
## Code to gather data from Alma Analytics and Upload to Data.World
## CREATED: jwammerman (jwacooks) 2017-10-27
## EDITED: aidans (atla5) 2019-01
"""
# import datadotworld as dw
from pandas import DataFrame
from time import sleep
from urllib.parse import urlencode, quote_plus
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from services.service import Service, get_api_key
from services.alma import CONTENT_TYPE_XML

DEFAULT_LIMIT = 1000
NS = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
KEY = get_api_key("alma", "analytics", "production")

# paths
UPLOAD_DESTINATION = "jwasys/bu-lib-stats"
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


def is_report_finished(report):
    return report.find('*/IsFinished').text != 'false'


class AlmaAnalytics(Service):

    def __init__(self, use_production=False, logging=True):
        super(AlmaAnalytics, self).__init__(use_production, logging)  # properly subclass from Service
        self.base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
        self.api_key = KEY

    def prepare_df_from_report_path(self, reportPath,  secondsBetweenRequests=2):
        self.log_message("requesting report for the first time by the reportPath")
        report = self.request_analytics_report_by_path(reportPath)

        # if the report isn't finished, use its 'ResumptionToken' to keep re-asking about it until it is
        while not is_report_finished(report):
            sleep(secondsBetweenRequests)
            self.log_message("re-requesting report via the 'ResumptionToken'...")
            resumption_token = report.find('*/ResumptionToken').text
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
            for col in row.getchildren():
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


if __name__ == "__main__":
    alma_analytics_svc = AlmaAnalytics(use_production=True)
    report_request_data = REPORTS_DICTIONARY["circulation_stats"]
    report_response_data = alma_analytics_svc.prepare_df_from_report_path(report_request_data["path"])
    report_response_data.to_csv(report_request_data["output"], sep='\t')


def old_code():
    ## code for OpenUrl Article Title statistics
    path = '%2Fshared%2FBoston%20University%2FReports%2Fjwa%2FTop%20ten%20article%20title%20accesses%20via%20OpenURL'
    df1 = DataFrame()
    limit = '100'
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode({quote_plus('apikey'): KEY, quote_plus('limit'): limit})
    queryParams += '&path=' + path

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    resp = ET.fromstring(response_body)
    ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
    isFinished = resp.find('*/IsFinished').text
    token = resp.find('*/ResumptionToken').text
    results = resp.find('*/ResultXml')
    rows = results.findall('*/ns0:Row', ns)
    row_dict = {}
    for row in rows:
        for col in row.getchildren():
            row_dict[col.tag[-7:]] = col.text
        row_dict
        df1 = df1.append(row_dict, ignore_index=True)

    columns = []
    resultXml = resp.findall('./*/ResultXml')[0]
    rowset = resultXml.find('./{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
    sequence = rowset.findall('./*/*/*/*')
    for el in sequence:
        columns.append(el.attrib['{urn:saw-sql}columnHeading'].replace(' REPORT_SUM(', '').replace(' Name)', ''))
    while isFinished == 'false':
        print(df1.shape[0])
        sleep(1)
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
        queryParams = '?' + urlencode(
            {quote_plus('token'): token, quote_plus('apikey'): KEY})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        resp = ET.fromstring(response_body)
        ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
        isFinished = resp.find('*/IsFinished').text
        results = resp.find('*/ResultXml')
        rows = results.findall('*/ns0:Row', ns)
        row_dict = {}
        for row in rows:
            for col in row.getchildren():
                row_dict[col.tag[-7:]] = col.text
            row_dict
            df1 = df1.append(row_dict, ignore_index=True)
    print('total: ', df1.shape[0])
    df1.columns = columns
    df1.head()

    df1.to_csv('open_url_article_stats.tsv', sep='\t')

    ## code for OpenUrl Journal Title statistics
    path = '%2Fshared%2FBoston%20University%2FReports%2Fjwa%2FTop%20ten%20title%20accesses%20via%20OpenURL%20requests'
    df1 = DataFrame()
    limit = '100'
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode({quote_plus('apikey'): KEY, quote_plus('limit'): limit})
    queryParams += '&path=' + path

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    resp = ET.fromstring(response_body)
    ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
    token = resp.find('*/ResumptionToken').text
    isFinished = resp.find('*/IsFinished').text
    results = resp.find('*/ResultXml')
    rows = results.findall('*/ns0:Row', ns)
    row_dict = {}
    for row in rows:
        for col in row.getchildren():
            row_dict[col.tag[-7:]] = col.text
        row_dict
        df1 = df1.append(row_dict, ignore_index=True)

    columns = []
    resultXml = resp.findall('./*/ResultXml')[0]
    rowset = resultXml.find('./{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
    sequence = rowset.findall('./*/*/*/*')
    for el in sequence:
        columns.append(el.attrib['{urn:saw-sql}columnHeading'].replace(' REPORT_SUM(', '').replace(' Name)', ''))
    while isFinished == 'false':
        print(df1.shape[0])
        sleep(1)
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
        queryParams = '?' + urlencode(
            {quote_plus('token'): token, quote_plus('apikey'): KEY})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        resp = ET.fromstring(response_body)
        ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
        isFinished = resp.find('*/IsFinished').text
        results = resp.find('*/ResultXml')
        rows = results.findall('*/ns0:Row', ns)
        row_dict = {}
        for row in rows:
            for col in row.getchildren():
                row_dict[col.tag[-7:]] = col.text
            row_dict
            df1 = df1.append(row_dict, ignore_index=True)
    print('total: ', df1.shape[0])
    df1.columns = columns
    df1.head()

    df1.to_csv('open_url_title_stats.tsv', sep='\t')

    ## code for OpenUrl Request statistics
    path = '%2Fshared%2FBoston%20University%2FReports%2Fjwa%2FOpenURL%20requests'
    df1 = DataFrame()
    limit = '100'
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode({quote_plus('apikey'): KEY, quote_plus('limit'): limit})
    queryParams += '&path=' + path

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    resp = ET.fromstring(response_body)
    ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
    token = resp.find('*/ResumptionToken').text
    isFinished = resp.find('*/IsFinished').text
    results = resp.find('*/ResultXml')
    rows = results.findall('*/ns0:Row', ns)
    row_dict = {}
    for row in rows:
        for col in row.getchildren():
            row_dict[col.tag[-7:]] = col.text
        row_dict
        df1 = df1.append(row_dict, ignore_index=True)

    columns = []
    resultXml = resp.findall('./*/ResultXml')[0]
    rowset = resultXml.find('./{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
    sequence = rowset.findall('./*/*/*/*')
    for el in sequence:
        columns.append(el.attrib['{urn:saw-sql}columnHeading'].replace(' REPORT_SUM(', '').replace(' Name)', ''))
    while isFinished == 'false':
        print(df1.shape[0])
        sleep(1)
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
        queryParams = '?' + urlencode(
            {quote_plus('token'): token, quote_plus('apikey'): KEY})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        resp = ET.fromstring(response_body)
        ns = {'ns0': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
        isFinished = resp.find('*/IsFinished').text
        results = resp.find('*/ResultXml')
        rows = results.findall('*/ns0:Row', ns)
        row_dict = {}
        for row in rows:
            for col in row.getchildren():
                row_dict[col.tag[-7:]] = col.text
            row_dict
            df1 = df1.append(row_dict, ignore_index=True)
    print('total: ', df1.shape[0])
    df1.columns = columns
    df1.head()

    df1.to_csv('open_url_request_stats.tsv', sep='\t')
    # api_client = dw.api_client()
    # api_client.create_dataset('jwasys', title='bu-lib-stats', visibility='PRIVATE',license='Public Domain')
    # api_client.upload_files('jwasys/bu-lib-stats',
    #                        ['open_url_request_stats.tsv', 'circ_stats.tsv', 'open_url_article_stats.tsv',
    #                         'open_url_title_stats.tsv'])

