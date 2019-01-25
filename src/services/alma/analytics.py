"""
## Code to gather data from Alma Analytics and Upload to Data.World
## CREATED: jwammerman (jwacooks) 2017-10-27
## EDITED: aidans (atla5) 2019-01
"""

## Load the required libraries
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
import time
import pandas as pd
import xml.etree.ElementTree as ET
import datadotworld as dw

from services import get_api_key

KEY = get_api_key("alma", "analytics", "production")  # no 'sandbox' for the alma analytics API

## code for circulation statistics
df = pd.DataFrame()
path = '%2Fshared%2FBoston%20University%2FReports%2Fjwa%2FNumberOfLoansPast7days'
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
    df = df.append(row_dict, ignore_index=True)

columns = []
resultXml = resp.findall('./*/ResultXml')[0]
rowset = resultXml.find('./{urn:schemas-microsoft-com:xml-analysis:rowset}rowset')
sequence = rowset.findall('./*/*/*/*')
for el in sequence:
    columns.append(el.attrib['{urn:saw-sql}columnHeading'].replace(' REPORT_SUM(', '').replace(' Name)', ''))
while isFinished == 'false':
    print(df.shape[0])
    time.sleep(1)
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode(
        {quote_plus('token'): token, quote_plus('apikey'): 'l7xxc0dce20e96bf431f980f3d0f0bb75917'})
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
        df = df.append(row_dict, ignore_index=True)
print('total: ', df.shape[0])
df.columns = columns
df.head()

df.to_csv('circ_stats.tsv', sep='\t')

## code for OpenUrl Article Title statistics
path = '%2Fshared%2FBoston%20University%2FReports%2Fjwa%2FTop%20ten%20article%20title%20accesses%20via%20OpenURL'
df1 = pd.DataFrame()
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
    print(df.shape[0])
    time.sleep(1)
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode(
        {quote_plus('token'): token, quote_plus('apikey'): 'l7xxc0dce20e96bf431f980f3d0f0bb75917'})
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
df1 = pd.DataFrame()
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
    print(df.shape[0])
    time.sleep(1)
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode(
        {quote_plus('token'): token, quote_plus('apikey'): 'l7xxc0dce20e96bf431f980f3d0f0bb75917'})
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
df1 = pd.DataFrame()
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
    print(df.shape[0])
    time.sleep(1)
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams = '?' + urlencode(
        {quote_plus('token'): token, quote_plus('apikey'): 'l7xxc0dce20e96bf431f980f3d0f0bb75917'})
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
api_client = dw.api_client()
# api_client.create_dataset('jwasys', title='bu-lib-stats', visibility='PRIVATE',license='Public Domain')
api_client.upload_files('jwasys/bu-lib-stats',
                        ['open_url_request_stats.tsv', 'circ_stats.tsv', 'open_url_article_stats.tsv',
                         'open_url_title_stats.tsv'])

