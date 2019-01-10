"""
## classes and functions for working with Primo
## jwammerman
## September 2019
"""

from urllib.request import Request, urlopen
from urllib.parse import quote_plus


class Primo:
    '''
    Primo is a set of tools to search Primo records
    '''

    def __init__(self):
        pass
        return

    def build_url(search_string, bulkSize):
        '''
        Function: build_url

        Purpose: Returns properly formatted url for a search string passed as the search_string parameter.
                 The url is built using the following variables defined in the class:
                 url_base
                 institution
                 bulkSize
                 onCampus
                 scope

         Parameter:  search_string
                     This is typically passed from a list of search strings

        '''
        url_base = 'http://bu-primo.hosted.exlibrisgroup.com/PrimoWebServices/xservice/search/brief'
        query_Params1 = '?institution=BOSU&query=any,contains,'
        query_Params2 = '&indx=1&bulkSize=' + bulkSize
        query_Params3 = '&loc=local,scope:(ALMA_BOSU1)&loc=adaptor,primo_central_multiple_fe&onCampus=true&json=true'
        url = url_base + query_Params1 + quote_plus(search_string.replace('  ', ' ')) + query_Params2 + query_Params3
        return (url)

    def get_primo_results(url):
        '''get_primo_results executes the search and returns the response'''
        request = Request(url)
        try:
            response_body = urlopen(request).read()
        except Exception as e:
            response_body = ''

        return response_body

    def get_primo_json(json_str):
        '''get_primo_json parses the primo result string'''
        total_hits = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['@TOTALHITS']
        if total_hits == '0':
            return (total_hits)
            # return('none')
        if int(total_hits) == 1:
            # print(total_hits)
            num_recs = 1
            sourceID = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['control'][
                'sourceid']
            delCat = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['delivery'][
                'delcategory']
            try:
                recordid = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search'][
                    'addsrcrecordid']  # .keys()
            except KeyError as e:
                recordid = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search'][
                    'recordid']  # .keys()
            #        almaMMS_ID = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search']['addsrcrecordid'] #.keys()
            title = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search'][
                'title']
            creationDate = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search'][
                'creationdate']  # .keys()
            creators = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC']['PrimoNMBib']['record']['search'][
                'creatorcontrib']
            # print(num_recs)
            # print(sourceID)
            # print(delCat)
            # print(recordid)
            # print(title)
            # print(creators)
            # print(creationDate)
            # print()
        else:
            try:
                num_recs = len(json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'])
            except Exception as e:
                print(e)
                print(total_hits)

            for i in range(0, num_recs):

                sourceID = \
                json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['control'][
                    'sourceid']
                delCat = \
                json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['delivery'][
                    'delcategory']
                try:
                    recordid = \
                    json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['search'][
                        'addsrcrecordid']  # .keys()
                except KeyError as e:
                    recordid = \
                    json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['search'][
                        'recordid']  # .keys()

                title = json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['search'][
                    'title']
                creationDate = \
                json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['search'][
                    'creationdate']  # .keys()
                creators = \
                json_str['SEGMENTS']['JAGROOT']['RESULT']['DOCSET']['DOC'][i]['PrimoNMBib']['record']['search'][
                    'creatorcontrib']
                # print(num_recs)
                # print(sourceID)
                # print(delCat)
                # print(almaMMS_ID)
                # print(title)
                # print(creators)
                # print(creationDate)
                # print()
        return (num_recs, sourceID, delCat, recordid, title, creators, creationDate)
