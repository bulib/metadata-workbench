from bs4 as BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus

import re
import time
import xml.etree.ElementTree as ET


fileout = open('springer_sbox_test_output.txt', 'w') #output file
print(fileout) 

## select either the sandbox key (sb_key) or the production key (prod_key)
## best to test with sb_ke
bib_api_key = "REDACTED"


def get_portfolios(mms_id):
	time.sleep(1)
	url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/portfolios'.replace('{mms_id}',quote_plus(mms_id))
	
	queryParams = '?' + urlencode({ quote_plus('apikey') : bib_api_key  })
	request = Request(url + queryParams)
	request.get_method = lambda: 'GET'
	response_body = urlopen(request).read()

	portfolios=ET.fromstring(response_body)
	pos = 0

	arr=[]
	arr2=[]
	while pos < len(portfolios):
		print('pos is:', pos)
		
		collection = portfolios[pos].find('./electronic_collection/id').text
		portfolio_id = portfolios[pos].find('./id').text
		arr.append(collection+'^'+portfolio_id)
		#arr2.append(collection)
		#print('portfolio id is:',portfolio_id)
		
		pos+=1
	return(arr)
	
	

def get_full_portfolio(mms_id,full_port_id):
	time.sleep(1)
	url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/portfolios/{full_port_id}'.replace('{mms_id}',quote_plus(mms_id)).replace('{full_port_id}',quote_plus(full_port_id))
	queryParams = '?' + urlencode({ quote_plus('view') : 'full' ,quote_plus('apikey') : bib_api_key  })
	request = Request(url + queryParams)
	request.get_method = lambda: 'GET'
	response_body = urlopen(request).read()
	full_portfolio=ET.fromstring(response_body)
	#ET.dump(full_portfolio)
	return(full_portfolio)


##collection_id='61764142980001161'
##collection_id='61905826220001161' 
collection_id='61777841160001161' #sbox springer ebooks
service_id='62777841150001161'

##mms_id = '99198693630001161'
##mms_id = '99208594151201161'
mms_id = '99208472396901161' #sbox example loaded by TL


ports=get_portfolios(mms_id)
print(ports)
lis=[p.split('^') for p in ports] 
for i,x in enumerate(lis):
	if lis[i][0]==collection_id:
		(lis[i]).append(mms_id)
		print(lis[i])
		full_port_id=lis[i][1]
		#print(full_port_id)
		full_portfolio=get_full_portfolio(mms_id,full_port_id)
		#ET.dump(full_portfolio)
		print('mms_id is:',mms_id)
		print('full_port_id is:', full_port_id)
		#print('full_portfolio is;',full_portfolio)
		static_url = full_portfolio.find('./linking_details/static_url').text
		static_url=static_url.replace('jkey=','')
		print('static url is:',static_url)

		try:
			request = Request(static_url)
			request.get_method = lambda: 'GET'
			response_body = urlopen(request).read()
			soup = BeautifulSoup(response_body, 'html.parser')
			print(soup.title)
			htitle=soup.title
			htitle=soup.title.text
			htitle = re.sub('[\r\n]','',htitle)
			fileout.write('DOI URL okay'+'\t'+mms_id+'\t'+full_port_id +'\t'+static_url+'\t'+htitle+'\n')
	
		except:
			print(static_url)
			print("error")
			urlm=static_url.replace('doi.org', 'link.springer.com/book')
	
			try:
				request = Request(urlm)
				request.get_method = lambda: 'GET'
				response_body = urlopen(request).read()
				soup = BeautifulSoup(response_body, 'html.parser')
				print(urlm)
				#print(soup.title)
				htitle=soup.title.text
				htitle = re.sub('[\r\n]','',htitle)
				
				#fileout.write(auth+'\t'+title+'\t'+mms_id+'\t'+'pid'+'\tURL modified\t'+urlm+'\t'+htitle+'\n')
				fileout.write('modified URLokay\t'+mms_id+'\t'+full_port_id+'\t'+urlm+'\t'+htitle+'\n')
			except:
				print('modified URL NOT okay')
				fileout.write('modified URL NOT okay\t'+mms_id+'\t'+full_port_id+'\t'+urlm+'\t \n')

		