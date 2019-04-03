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
from src.services import OUTPUT_DIRECTORY, construct_log_message

# output url_status values
STATUS_OKAY = 'DOI URL okay'
STATUS_REPAIRED = 'modified URLokay'
STATUS_BROKEN = 'modified URL not okay'

# setup the output file
OUTPUT_FILENAME = 'springer_sbox_test_output.txt'
output_path = join(OUTPUT_DIRECTORY, OUTPUT_FILENAME)
output_file = open(output_path, 'w')


# collection_id='61764142980001161'
# collection_id='61905826220001161'
collection_id = '61777841160001161'  # sbox springer ebooks

# mms_id = '99198693630001161'
# mms_id = '99208594151201161'
mms_id = '99208472396901161'  # sbox example loaded by TL


def log_message(message):
	print(construct_log_message(__file__, message))


alma_bibs_service = AlmaBibs(use_production=False, logging=True)
log_message("obtaining portfolios for mms_id '" + mms_id + "'")

ports = alma_bibs_service.get_portfolios_from_mmsid(mms_id)

lis = [p.split('^') for p in ports]
csv_heading = "url_status\tmms_id\tportfolio id\turl\ttitle\n"
output_file.write(csv_heading)
for i, x in enumerate(lis):
	if lis[i][0] == collection_id:
		(lis[i]).append(mms_id)

		full_port_id = lis[i][1]
		full_portfolio = alma_bibs_service.get_full_portfolio(mms_id, full_port_id)

		static_url = full_portfolio.find('./linking_details/static_url').text
		static_url = static_url.replace('jkey=', '')

		url_status = STATUS_OKAY
		url_final = static_url
		title = ""
		try:
			request = Request(static_url)
			request.get_method = lambda: 'GET'
			response_body = urlopen(request).read()
			soup = BeautifulSoup(response_body, 'html.parser')

			htitle = soup.title.text
			htitle = re.sub('[\r\n]', '', htitle)

			url_status = STATUS_OKAY
			title = htitle
	
		except:
			modified_url = static_url.replace('doi.org', 'link.springer.com/book')
			url_final = modified_url
	
			try:
				request = Request(modified_url)
				request.get_method = lambda: 'GET'
				response_body = urlopen(request).read()
				soup = BeautifulSoup(response_body, 'html.parser')

				htitle = soup.title.text
				htitle = re.sub('[\r\n]', '', htitle)

				url_status = STATUS_REPAIRED
				title = htitle
			except:
				url_status = STATUS_BROKEN
				title = ""
		finally:
			csv_row = "{url_status}\t{mms_id}\t{port_id}\t{url}\t{title}\n".format(
				url_status=url_status, mms_id=mms_id, port_id=full_port_id, url=url_final, title=title
			)
			alma_bibs_service.log_message("url_status for portfolio_id '{}': '{}'".format(full_port_id, url_status))
			output_file.write(csv_row)

log_message("script completed. see '{}' for output log".format(OUTPUT_FILENAME))
