"""
## find and repair broken urls in springer book portfolios
## CREATED: tim lewontin (ashpyth) 2019-04
## EDITED: aidans (atla5) 2019-04
"""

from bs4 import BeautifulSoup
from os.path import join
from re import sub

from src.services.bibs import AlmaBibs
from src.services import OUTPUT_DIRECTORY, construct_log_message, make_basic_request

# settings
REQUEST_REMOTE_UPDATE = False

# output url_status values
STATUS_OKAY = "OKAY"  # DOI URL was fine to begin with
STATUS_TO_REPLACE = "TO_REPLACE"  # the substitute URL works and its ready to manually update
STATUS_REPAIRED = "REPAIRED"  # successfully repaired the portfolio remotely
STATUS_FAILED = "FAILED_ATTEMPT"  # tried to update alma with new (valid) url, but couldn't do it
STATUS_BROKEN = "BROKEN"  # even the modified url didn't work, so it needs fixing another way

# sample MMS_IDs
SAMPLE_MMS_ID_OKAY = '99208472396901161'
SAMPLE_MMS_ID_REPAIRED = '99208472396401161'
SAMPLE_MMS_ID_BROKEN = ''


def log_message(message):
	print(construct_log_message(__file__, message))


def get_page_title_from_response(response):
	soup = BeautifulSoup(response, 'html.parser')
	htitle = soup.title.text
	htitle = sub('[\r\n]', '', htitle)
	return htitle


def process_list_of_mms_ids(ls_mms_ids, csv_file):
	for mms_id in ls_mms_ids:
		process_mms_id(mms_id, csv_file=csv_file)
	log_message("script completed. see '{}' for output log".format(csv_file.name))


def process_mms_id(mms_id, csv_file):
	alma_bibs_service = AlmaBibs(use_production=False, logging=True)
	log_message("obtaining portfolios for mms_id '" + mms_id + "'")

	ls_portfolio_ids = alma_bibs_service.get_portfolios_from_mmsid(mms_id)
	for portfolio_id in ls_portfolio_ids:
		full_portfolio = alma_bibs_service.get_full_portfolio(mms_id, portfolio_id)

		static_url = full_portfolio.find('./linking_details/static_url').text
		static_url = static_url.replace('jkey=', '')

		# make initial request to listed 'static_url' and mark it as okay if there aren't any exceptions
		url_status = url_final = title = ""
		try:
			response_body = make_basic_request(static_url)
			title = get_page_title_from_response(response_body)
			url_final = static_url
			url_status = STATUS_OKAY

		except:  # if that link fails, modify the url and see if that does it...
			modified_url = static_url.replace('doi.org', 'link.springer.com/book')
			url_final = modified_url

			try:  # if the new request succeeds, mark it as repaired
				response_body = make_basic_request(modified_url)
				title = get_page_title_from_response(response_body)
				url_status = STATUS_TO_REPLACE

				if REQUEST_REMOTE_UPDATE:
					before = full_portfolio.find('./linking_details/static_url').text
					full_portfolio.find('./linking_details/static_url').text = "jkey={}".format(modified_url)
					after = full_portfolio.find('./linking_details/static_url').text
					log_message("before: '{}', after: '{}'".format(before, after))

					request_succeeded = alma_bibs_service.update_portfolio(mms_id, portfolio_id, full_portfolio)
					if request_succeeded:
						url_status = STATUS_REPAIRED
					else:
						url_status = STATUS_FAILED

			except:  # if the modified url _doesn't_ work, mark it as broken
				title = ""
				url_status = STATUS_BROKEN
		finally:
			csv_row = "{url_status}\t{mms_id}\t{port_id}\t{url}\t{title}\n".format(
				url_status=url_status, mms_id=mms_id, port_id=portfolio_id, url=url_final, title=title
			)
			alma_bibs_service.log_message("url_status for portfolio_id '{}': '{}'".format(portfolio_id, url_status))
			csv_file.write(csv_row)


if __name__ == "__main__":

	# create output file
	output_filename = 'springer_sbox_test_output.tsv'
	output_path = join(OUTPUT_DIRECTORY, output_filename)
	output_file = open(output_path, 'w')

	# print out heading of the CSV file
	csv_heading = "url_status\tmms_id\tportfolio id\turl\ttitle\n"
	output_file.write(csv_heading)

	# get input file
	input_filename = "update-portfolio_sbox-test-set.csv"
	input_path = join(OUTPUT_DIRECTORY, "..", "input", input_filename)
	input_file = open(input_path, 'r')

	mms_ids = []
	first_line = True
	for line in input_file:
		if not first_line:
			mms_ids.append(line.split(',')[0])
		first_line = False
	input_file.close()

	# process a list
	# ls_mms_id = [SAMPLE_MMS_ID_OKAY, SAMPLE_MMS_ID_REPAIRED, SAMPLE_MMS_ID_BROKEN]
	process_list_of_mms_ids(mms_ids, output_file)

	# process single one
	# process_mms_id(SAMPLE_MMS_ID_OKAY, output_file)
	output_file.close()

