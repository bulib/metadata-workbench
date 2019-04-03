"""
## find and repair broken urls in springer book portfolios
## CREATED: tim lewontin (ashpyth) 2019-04
## EDITED: aidans (atla5) 2019-04
"""

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from os.path import join
import re

from src.services.bibs import AlmaBibs
from src.services import OUTPUT_DIRECTORY

OUTPUT_FILENAME = 'springer_sbox_test_output.txt'
output_path = join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)
fileout = open(output_path, 'w')  # output file


# collection_id='61764142980001161'
# collection_id='61905826220001161'
collection_id = '61777841160001161'  # sbox springer ebooks
service_id = '62777841150001161'

# mms_id = '99198693630001161'
# mms_id = '99208594151201161'
mms_id = '99208472396901161'  # sbox example loaded by TL


alma_bibs_service = AlmaBibs(use_production=False, logging=True)
ports = alma_bibs_service.get_portfolios_from_mmsid(mms_id)

lis = [p.split('^') for p in ports]
for i, x in enumerate(lis):
	if lis[i][0] == collection_id:
		(lis[i]).append(mms_id)

		full_port_id = lis[i][1]
		alma_bibs_service.log_message("portfolio_id: " + full_port_id)

		full_portfolio = alma_bibs_service.get_full_portfolio(mms_id, full_port_id)

		alma_bibs_service.log_message('mms_id is:' + mms_id)
		alma_bibs_service.log_message('full_port_id is: ' + full_port_id)

		static_url = full_portfolio.find('./linking_details/static_url').text
		static_url = static_url.replace('jkey=', '')
		print('static url is:', static_url)

		try:
			request = Request(static_url)
			request.get_method = lambda: 'GET'
			response_body = urlopen(request).read()
			soup = BeautifulSoup(response_body, 'html.parser')

			htitle = soup.title.text
			htitle = re.sub('[\r\n]', '', htitle)
			csv_row = "DOI URL okay\t{mms_id}\t{port_id}\t{url}\t{htitle}\n".format(mms_id=mms_id, port_id=full_port_id, url=static_url, htitle=htitle)
			fileout.write(csv_row)
	
		except:
			print(static_url)
			urlm = static_url.replace('doi.org', 'link.springer.com/book')
	
			try:
				request = Request(urlm)
				request.get_method = lambda: 'GET'
				response_body = urlopen(request).read()
				soup = BeautifulSoup(response_body, 'html.parser')

				print("modified url: " + urlm)
				# print(soup.title)

				htitle = soup.title.text
				htitle = re.sub('[\r\n]', '', htitle)
				
				# prepare write-up
				csv_row = "modified URLokay\t{mms_id}\t{port_id}\t{url}\t{title}\n".format(mms_id=mms_id, port_id=full_port_id, url=urlm, title=htitle)
				fileout.write(csv_row)
			except:
				csv_row = "modified URL NOT okay\t{mms_id}\t{port_id}\t{url}\t{title}\n".format(mms_id=mms_id, port_id=full_port_id, url=urlm, title=" ")
				fileout.write(csv_row)
