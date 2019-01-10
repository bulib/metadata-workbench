"""
## classes and functions for working with Alma
## jwammerman
## September 2019
"""

from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
from lxml import etree


def get_alma_key(api, platform):
    '''get_key(api,platform):
       get_key loads the api keys file and returns the requested key
       requires two parameters passed as strings:
       api : 'analytics', 'bib', 'config', 'courses', 'users'or 'electronic'
       platform : 'production' or 'sandbox'
    '''
    import json
    # from pprint import pprint
    with open('/Users/jwa/keys/alma_api_keys.json') as f:
        data = json.load(f)
    # pprint(data)
    return data['alma'][api][platform]


class Alma:
    '''Alma is a set of tools for adding and manipulating Alma bib records'''
    def __init__(self):
        pass
        return

    def get_bib_from_alma(mms_id, key):
        '''get_bib_from_alma(mms_id,key):
        retrieve a bib record from alma. Requires mms_id and api_key
        returns the bib object in xml
        '''
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}'.replace('{mms_id}', quote_plus(mms_id))
        queryParams = '?' + urlencode({quote_plus('expand'): 'None', quote_plus('apikey'): key})  ## production
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        bib = etree.fromstring(response_body)
        return (bib)

    def update_bib_in_alma(mms_id, bib, key):
        '''update_bib_in_alma(mms_id,bib,key):
        update a bib record in alma. Requires:
        mms_id,
        a bib object (xml)
        api_key
        returns the updated bib object in xml with validation warnings
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}'.replace('{mms_id}', quote_plus(mms_id))
        queryParams = '?' + urlencode(
            {quote_plus('validate'): 'true', quote_plus('stale_version_check'): 'false', quote_plus('apikey'): key})
        values = etree.tostring(bib)
        headers = {'Content-Type': 'application/xml'}
        request = Request(url + queryParams
                          , data=values
                          , headers=headers)
        request.get_method = lambda: 'PUT'
        response_body = urlopen(request).read()
        bib = etree.fromstring(response_body)
        return (bib)

    def get_marc_fields(tag, bib):
        '''
        get_marc_fields():
        retrieves all instances of a marc tag from a bib record. Require:
        tag - as a string (ex: '008', '020', '650')
        bib - the bibliographic record as an xml object
        returns a list of xml elements containing the marc tag
        '''
        fields = bib.findall("*/[@tag='" + tag + "']")
        return (fields)

    def has_marc_field(tag, bib):
        '''
        has_marc_field():
        Verifies the presence of a marc field. Require:
        tag - as a string (ex: '008', '020', '650')
        bib - the bibliographic record as an xml object
        returns True if the tag exists, False if the tag does not exist
        '''
        field = bib.find("*/[@tag='" + tag + "']")
        return (type(field) == etree.Element)

    def get_holdings_list_for_bib(mms_id, key):
        '''
        get_holdings_list_for_bib(mms_id,key):
        retrieves a list of holdings attached to the bib record. Requires:
        mms_id
        api_key
        Returns an xml holdings list element
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings'.replace('{mms_id}',
                                                                                                 quote_plus(mms_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        holdings_list = etree.fromstring(response_body)
        return (holdings_list)

    def get_holdings_record(mms_id, holdings_id, key):
        '''
        get_holdings_record(mms_id,key):
        retrieves a holdings record attached to the bib record. Requires:
        mms_id
        holdings_id
        api_key
        Returns an xml holdings element element
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}'.replace(
            '{mms_id}', quote_plus(mms_id)).replace('{holding_id}', quote_plus(holdings_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        holdings = etree.fromstring(response_body)
        return (holdings)

    def update_holdings_record(mms_id, holdings_id, holdings_object, key):
        '''
        update_holdings_record(mms_id,holdings_id,holdings_object,key):
        updates a holdings record. Requires:
        mms_id
        holdings_id
        holdings_object as an xml holdings element
        api_key
        Returns: updated holdings object
        '''
        holdings_object = etree.tostring(holdings_object)
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}'.replace(
            '{mms_id}', quote_plus(mms_id)).replace('{holding_id}', quote_plus(holdings_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})
        values = holdings_object
        headers = {'Content-Type': 'application/xml'}
        request = Request(url + queryParams
                          , data=values
                          , headers=headers)
        request.get_method = lambda: 'PUT'
        response_body = urlopen(request).read()
        holdings = etree.fromstring(response_body)
        return (holdings)

    def delete_holdings_record(mms_id, holdings_id, bib_method, key):
        '''
        delete_holdings_record(mms_id,holdings_id,bib_method,key):
        deletes a holdings record. Required:
        mms_id
        holdings_id
        bib_method (Method for handling a Bib record left without any holdings: retain, delete or suppress)
        api_key
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}'.replace(
            '{mms_id}', quote_plus(mms_id)).replace('{holding_id}', quote_plus(holdings_id))
        queryParams = '?' + urlencode({quote_plus('bib'): bib_method, quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'DELETE'
        response_body = urlopen(request).read()
        return (response_body)

    def get_items_list(mms_id, holdings_id, limit, offset, key):
        '''
        get_items_list(mms_id,holdings_id,limit,offset,key):
        retrieve a list of item records attached to a holdings record. Required:
        mms_id
        holdings_id
        limit (the string representation of the maximum number of records to be returned)
        offset (the string representation of the offset in the record list to begin returning records)
        api_key
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}/items'.replace(
            '{mms_id}', quote_plus(mms_id)).replace('{holding_id}', quote_plus(holdings_id))
        queryParams = '?' + urlencode(
            {quote_plus('limit'): limit, quote_plus('offset'): offset, quote_plus('order_by'): 'none',
             quote_plus('direction'): 'desc', quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        items_list = etree.fromstring(response_body)
        return (items_list)

    def get_representations_list(mms_id, limit, offset, key):
        '''
        get_representations_list(mms_id, limit, offset, key):
        retrieve a list of digital representations attached to a bib record. Required:
        mms_id
        limit (the string representation of the maximum number of records to be returned)
        offset (the string representation of the offset in the record list to begin returning records)
        api_key
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/representations'.replace('{mms_id}',
                                                                                                        quote_plus(
                                                                                                            mms_id))
        queryParams = '?' + urlencode(
            {quote_plus('limit'): limit, quote_plus('offset'): offset, quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        representations_list = etree.fromstring(response_body)
        return (representations_list)

    def get_representation(mms_id, rep_id, key):
        '''
        get_representation(mms_id,rep_id,key):
        retrieve the digital representation record. Required:
        mms_id
        representation_id
        api_key
        '''
        url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/representations/{rep_id}'.replace(
            '{mms_id}', quote_plus(mms_id)).replace('{rep_id}', quote_plus(rep_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
        representation = etree.fromstring(response_body)
        return (representation)

    def add_ia_representation(mms_id, identifier, rights, key):
        '''add_representation adds a digital reprentation record to a bib record in Alma for a
        digital object residing in an institutional repository
        Parameters:
            mms_id,
            identifier - the OAI record identifier
            rights - a string indicating the rights associated with the digital object
            key - the api_key
        Returns the mms_id, the OAI record identifier, and the ID for the digital representation'''
        if rights == 'pd':
            rights = 'Public Domain : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.'
        if rights == 'pdus':
            rights = "Public Domain (US) : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission in the U.S."
        if rights == 'cc-by-nc-nd-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.'
        if rights == 'cc-by-nc-nd-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.'
        if rights == 'cc-by-nc-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial license.'
        if rights == 'cc-by-nc-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-nc-sa-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-nc-sa-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution license.'
        if rights == 'cc-by-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution license.'

        delivery_url = identifier.replace('%3A', ':').replace('%2F', '/')
        linking_parameter = identifier
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/representations'.replace('{mms_id}',
                                                                                                        quote_plus(
                                                                                                            mms_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})
        values = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                 <representation is_remote="true">    
                 <id />    
                 <library desc="Mugar">MUG</library>    
                 <usage_type desc="Derivative">DERIVATIVE_COPY</usage_type> 
                 <public_note>{rights}</public_note>
                 <delivery_url>{delivery_url}</delivery_url>    
                 <thumbnail_url/>    
                 <repository desc="InternetArchive">InternetArchive</repository>  
                 <originating_record_id>{identifier}</originating_record_id>    
                 <linking_parameter_1>{linking_parameter}</linking_parameter_1>    
                 <linking_parameter_2/>    
                 <linking_parameter_3/>    
                 <linking_parameter_4/>    
                 <linking_parameter_5/>    
                 <created_by>jwasys</created_by>    
                 <created_date>2017-04-28Z</created_date>    
                 <last_modified_by>jwasys</last_modified_by>    
                 <last_modified_date>2017-04-28Z</last_modified_date>
                 </representation>'''
        values = values.replace('{mms_id}', quote_plus(mms_id)).replace('{identifier}', quote_plus(linking_parameter))
        values = values.replace('{rights}', rights).replace('\n', '')
        values = values.replace('{linking_parameter}', quote_plus(linking_parameter)).replace('{delivery_url}',
                                                                                              quote_plus(
                                                                                                  delivery_url)).encode(
            "utf-8")
        headers = {'Content-Type': 'application/xml'}
        request = Request(url + queryParams
                          , data=values
                          , headers=headers)
        request.get_method = lambda: 'POST'
        response_body = urlopen(request).read()
        tree = etree.fromstring(response_body)
        x = tree.find('id')
        return (mms_id, identifier, x.text)

    def add_ht_representation(mms_id, identifier, rights, key):
        '''add_representation adds a digital reprentation record to a bib record in Alma for a
        digital object residing in an institutional repository
        Parameters:
            mms_id,
            identifier - the OAI record identifier
            rights - a string indicating the rights associated with the digital object
            key - the api_key
        Returns the mms_id, the OAI record identifier, and the ID for the digital representation'''
        if rights == 'pd':
            rights = 'Public Domain : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.'
        if rights == 'pdus':
            rights = "Public Domain (US) : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission in the U.S."
        if rights == 'cc-by-nc-nd-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.'
        if rights == 'cc-by-nc-nd-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.'
        if rights == 'cc-by-nc-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial license.'
        if rights == 'cc-by-nc-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-nc-sa-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-nc-sa-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.'
        if rights == 'cc-by-3.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution license.'
        if rights == 'cc-by-4.0':
            rights += 'This work is protected by copyright law, but made available under a Creative Commons Attribution license.'

        delivery_url = identifier.replace('%3A', ':').replace('%2F', '/')
        linking_parameter = identifier
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/representations'.replace('{mms_id}',
                                                                                                        quote_plus(
                                                                                                            mms_id))
        queryParams = '?' + urlencode({quote_plus('apikey'): key})  ## production
        values = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                 <representation is_remote="true">    
                 <id />    
                 <library desc="Mugar">MUG</library>    
                 <usage_type desc="Derivative">DERIVATIVE_COPY</usage_type> 
                 <public_note>{rights}</public_note>
                 <delivery_url>{delivery_url}</delivery_url>    
                 <thumbnail_url/>    
                 <repository desc="HathiTrust">HathiTrust</repository>  
                 <originating_record_id>{identifier}</originating_record_id>    
                 <linking_parameter_1>{linking_parameter}</linking_parameter_1>    
                 <linking_parameter_2/>    
                 <linking_parameter_3/>    
                 <linking_parameter_4/>    
                 <linking_parameter_5/>    
                 <created_by>jwasys</created_by>    
                 <created_date>2017-04-28Z</created_date>    
                 <last_modified_by>jwasys</last_modified_by>    
                 <last_modified_date>2017-04-28Z</last_modified_date>
                 </representation>'''
        values = values.replace('{mms_id}', quote_plus(mms_id)).replace('{identifier}', quote_plus(linking_parameter))
        values = values.replace('{rights}', rights).replace('\n', '')
        values = values.replace('{linking_parameter}', quote_plus(linking_parameter)).replace('{delivery_url}',
                                                                                              quote_plus(
                                                                                                  delivery_url)).encode(
            "utf-8")
        headers = {'Content-Type': 'application/xml'}
        request = Request(url + queryParams
                          , data=values
                          , headers=headers)
        request.get_method = lambda: 'POST'
        # return(values)
        response_body = urlopen(request).read()
        tree = etree.fromstring(response_body)
        x = tree.find('id')
        return (mms_id, identifier, x.text)

    def sort_marc_tags(record):
        '''
        sort_marc_tags(record):
        sorts the marc tags in a record in numerical order. Requires:
        marc_xml bib record
        Returns the sorted marc_xml bib record
        '''
        data = []
        for elem in record.getchildren():
            if 'leader' in elem.tag:  # == 'http://www.loc.gov/MARC21/slim}leader':
                data.append(('000', elem))
            else:
                attrib = elem.attrib
                for k, v in attrib.items():
                    if k == 'tag':
                        data.append((v, elem))
        data = sorted(data, key=lambda x: x[0])
        new_rec = etree.Element('record')
        for i in data:
            new_rec.append(i[1])
        return (new_rec)

    def make_field(d, subfields):
        '''paramter d is a dictionary carrying the values for the marc field
        parameter subfields is a list of dicts carrying the values for the subfields'''
        if len(subfields) > 0:
            f = etree.Element('datafield')
            f.attrib['tag'] = d['tag']
            f.attrib['ind1'] = d['ind1']
            f.attrib['ind2'] = d['ind2']
            for sub in subfields:
                s = etree.Element('subfield')
                s.attrib['code'] = sub['code']
                s.text = sub['text']
                f.append(s)
        elif len(subfields) == 0:
            f = etree.Element('controlfield')
            f.attrib['tag'] = d['tag']
            f.attrib['ind1'] = d['ind1']
            f.attrib['ind2'] = d['ind2']
            f.text = d['text']
        else:
            print(len(subfields))
            print(subfields)
            pass
        return (f)
