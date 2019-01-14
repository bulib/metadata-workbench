"""
## classes and functions for working with Alma
## CREATED: jwammerman (jwacooks) 2018-09
## EDITED: aidans (atla5) 2019-01
"""

from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from lxml import etree
from time import strftime

from services import API_KEYS

# helpful reused variables
HTTP_TOO_MANY_REQUESTS = 429
CONTENT_TYPE_XML = {'Content-Type': 'application/xml'}
RIGHTS_DICTIONARY = {
    "pd": "Public Domain : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.",
    "pdus": "Public Domain (US) : You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission in the U.S.",
    "cc-by-nc-nd-3.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.",
    "cc-by-nc-nd-4.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-NoDerivatives license.",
    "cc-by-nc-3.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial license.",
    "cc-by-nc-4.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.",
    "cc-by-nc-sa-4.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.",
    "cc-by-nc-sa-3.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution-NonCommercial-ShareAlike license.",
    "cc-by-3.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution license.",
    "cc-by-4.0": "This work is protected by copyright law, but made available under a Creative Commons Attribution license."
}


def get_alma_key_from_path(apiPath, env="sandbox"):
    """get_key(api,platform):
       get_key loads the api keys file and returns the requested key
       requires two parameters passed as strings:
       apiPath : 'analytics', 'bib', 'config', 'courses', 'users'or 'electronic'
       environment : 'production' or 'sandbox'
    """
    api_path_fragment = apiPath.split("/")[1]
    alma_api = "config" if ("conf/" in apiPath) else api_path_fragment

    try:
        api_key = API_KEYS["alma"][alma_api][env]
    except KeyError:
        print("invalid key '" + alma_api + "'. defaulting to 'bibs' instead:")
        api_key = API_KEYS["alma"]["bibs"][env]

    return api_key


class Alma:
    """Alma is a set of tools for adding and manipulating Alma bib records"""
    def __init__(self, use_production=False, logging=True):
        self.env = "production" if use_production else "sandbox"
        self.log = logging

    def log_message(self, message, level="INFO"):
        if self.log:
            print("{}\t|{}\t|{}:{}".format(strftime('%Y-%m-%d %H:%M:%S'), level, "ALMA", message))

    def log_warning(self, message):
        linebreak = "-"*len(message)+"\n"
        self.log_message("{0}{1}\n{0}".format(linebreak, message), level="WARN")

    def make_request(self, apiPath, queryParams=None, method=lambda: 'GET', requestBody=None, headers=None):

        # build URL we'll be requesting to (note: we expect the apiPath to start with '/')
        api_key = get_alma_key_from_path(apiPath, self.env)
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1{api_path}?apiKey={api_key}'.format(
            api_path=apiPath, api_key=api_key
        )
        if queryParams:
            for key, value in queryParams.items():
                url += '&{}={}'.format(key, value)

        # build request
        data = requestBody if requestBody else {}
        headers = headers if headers else {}
        request = Request(url, data=data, headers=headers)
        request.get_method = method

        # send and store request
        self.log_message("making an alma request to '" + request.full_url + "'")
        response = urlopen(request)
        response_body = response.read().decode(response.headers.get_content_charset())

        if response.status == HTTP_TOO_MANY_REQUESTS:
            self.log_warning("WARNING! Received a 'Too Many Requests' response from alma! Please WAIT before retrying")
            exit(1)
        else:
            self.log_message("response code: " + str(response.status))

        return response_body

    def get_bib_record_by_mms_id(self, mms_id):
        """get_bib_from_alma(mms_id,key):
            Requires mms_id
            returns the bib object in xml
        """
        path = '/bibs/{mms_id}'.format(mms_id=mms_id)
        query_params = {"expand": "None"}
        response_body = self.make_request(path, query_params, headers=CONTENT_TYPE_XML)
        bib = etree.fromstring(response_body.encode())
        return bib

    def update_bib_record_by_mms_id(self, mms_id, bib):
        """update_bib_in_alma(mms_id,bib,key):
        update a bib record in alma.
        Requires:
            mms_id,
            a bib object (xml)
        returns the updated bib object in xml with validation warnings
        """
        path = '/bibs/{mms_id}'.format(mms_id=mms_id)
        queryParams = {
            "validate": "true",
            "stale_version_check": "false"
        }
        values = etree.tostring(bib)  # TODO resolve ValueError: 'Please use bytes input or XML fragments...
        response_body = self.make_request(path, queryParams, method=lambda: 'PUT',
                                          requestBody=values, headers=CONTENT_TYPE_XML)
        bib = etree.fromstring(response_body)
        return bib

    def get_holdings_list_for_bib(self, mms_id):
        """get_holdings_list_for_bib(mms_id,key):
        retrieves a list of holdings attached to the bib record.
        Requires: mms_id
        Returns an xml holdings list element
        """
        path = '/bibs/{mms_id}/holdings'.format(mms_id=mms_id)
        response_body = self.make_request(path, headers=CONTENT_TYPE_XML)
        holdings_list = etree.fromstring(response_body)  # TODO: resolve ValueError: 'Please use bytes input or XML...
        return holdings_list

    def get_holdings_record(self, mms_id, holdings_id):
        """get_holdings_record(mms_id,key):
        retrieves a holdings record attached to the bib record.
        Requires:
            mms_id
            holdings_id
        Returns an xml holdings element element
        """
        path = '/bibs/{mms_id}/holdings/{holdings_id}'.format(mms_id=mms_id, holdings_id=holdings_id)
        response_body = self.make_request(path, headers=CONTENT_TYPE_XML)
        holdings = etree.fromstring(response_body)
        return holdings

    def update_holdings_record(self, mms_id, holdings_id, holdings_object):
        """update_holdings_record(mms_id,holdings_id,holdings_object,key):
        Requires:
            mms_id
            holdings_id
            holdings_object as an xml holdings element
        Returns: updated holdings object
        """
        holdings_object = etree.tostring(holdings_object)
        path = '/bibs/{mms_id}/holdings/{holding_id}'.format(mms_id=mms_id, holding_id=holdings_id)

        response_body = self.make_request(path, method=lambda: 'PUT', headers=CONTENT_TYPE_XML,
                                          requestBody=holdings_object)
        holdings = etree.fromstring(response_body)
        return holdings

    def delete_holdings_record(self, mms_id, holdings_id, bib_method):
        """delete_holdings_record(mms_id,holdings_id,bib_method,key):
        Required:
            mms_id
            holdings_id
            bib_method (Method for handling a Bib record left without any holdings: retain, delete or suppress)
        """
        path = '/bibs/{mms_id}/holdings/{holding_id}'.format(mms_id=mms_id, holding_id=holdings_id)
        queryParams = {"bib": quote_plus(bib_method)}

        response_body = self.make_request(path, queryParams=queryParams, method=lambda: 'DELETE')
        return response_body

    def get_items_from_holdings_record(self, mms_id, holdings_id, limit, offset, order_by="none", direction="desc"):
        """get_items_list(mms_id,holdings_id,limit,offset,key):
        retrieve a list of item records attached to a holdings record.
        Required:
            mms_id
            holdings_id
            limit (the string representation of the maximum number of records to be returned)
            offset (the string representation of the offset in the record list to begin returning records)
        """
        path = '/bibs/{mms_id}/holdings/{holding_id}/items'.format(mms_id=mms_id, holding_id=holdings_id)
        queryParams = {
            "limit": limit,
            "offset": offset,
            "order_by": quote_plus(order_by),
            "direction": quote_plus(direction)
        }
        response_body = self.make_request(path, queryParams, headers=CONTENT_TYPE_XML)
        items_list = etree.fromstring(response_body)
        return items_list

    def get_representations_list(self, mms_id, limit, offset):
        """get_representations_list(mms_id, limit, offset, key):
        retrieve a list of digital representations attached to a bib record.
        Required:
            mms_id
            limit (the string representation of the maximum number of records to be returned)
            offset (the string representation of the offset in the record list to begin returning records)
        """
        path = '/bibs/{mms_id}/representations'.format(mms_id=mms_id)
        queryParams = {"limit": limit, "offset": offset}

        response_body = self.make_request(path, queryParams, headers=CONTENT_TYPE_XML)
        representations_list = etree.fromstring(response_body)
        return representations_list

    def get_representation(self, mms_id, rep_id):
        """get_representation(mms_id,rep_id):
        retrieve the digital representation record.
        Required:
            mms_id
            representation_id
        """
        path = '/bibs/{mms_id}/representations/{rep_id}'.format(mms_id=mms_id, rep_id=rep_id)
        response_body = self.make_request(path, headers=CONTENT_TYPE_XML)
        representation = etree.fromstring(response_body)
        return representation

    def add_ia_representation(self, mms_id, identifier, rights):
        """
        add_representation adds a digital representation record to a bib record in Alma for a
            digital object residing in an institutional repository
        Requires:
            mms_id,
            identifier - the OAI record identifier
            rights - a string indicating the rights associated with the digital object
        Returns the mms_id, the OAI record identifier, and the ID for the digital representation
        """
        rights = RIGHTS_DICTIONARY[rights]
        delivery_url = identifier.replace('%3A', ':').replace('%2F', '/')
        linking_parameter = identifier
        path = '/bibs/{mms_id}/representations'.format(mms_id=mms_id)

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
                <created_date>{yyyy_mm_dd}Z</created_date>    
                <last_modified_by>jwasys</last_modified_by>    
                <last_modified_date>{yyyy_mm_dd}Z</last_modified_date>
            </representation>'''.format(
                identifier=quote_plus(linking_parameter),
                mms_id=mms_id,
                rights=quote_plus(rights).replace('\n', ''),
                linking_parameter=quote_plus(linking_parameter),
                delivery_url=quote_plus(delivery_url),
                yyyy_mm_dd=strftime("%Y-%m-%d")
            )

        response_body = self.make_request(path, method=lambda: 'POST', headers=CONTENT_TYPE_XML,
                                          requestBody=values.encode("utf-8"))
        tree = etree.fromstring(response_body)
        x = tree.find('id')
        return (mms_id, identifier, x.text)

    def add_ht_representation(self, mms_id, identifier, rights):
        """
        add_representation adds a digital representation record to a bib record in Alma for a
            digital object residing in an institutional repository
        Parameters:
            mms_id,
            identifier - the OAI record identifier
            rights - a string indicating the rights associated with the digital object
        Returns the mms_id, the OAI record identifier, and the ID for the digital representation
        """
        rights = RIGHTS_DICTIONARY[rights]
        delivery_url = identifier.replace('%3A', ':').replace('%2F', '/')
        linking_parameter = identifier
        path = '/bibs/{mms_id}/representations'.format(mms_id=mms_id)

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
                <created_date>{yyyy_mm_dd}Z</created_date>    
                <last_modified_by>jwasys</last_modified_by>    
                <last_modified_date>{yyyy_mm_dd}Z</last_modified_date>
            </representation>'''.format(
            mms_id=mms_id,
            identifier=quote_plus(linking_parameter),
            rights=rights.replace('\n', ''),
            linking_parameter=quote_plus(linking_parameter),
            delivery_url=quote_plus(delivery_url),
            yyyy_mm_dd=strftime("%Y-%m-%d")
        )
        response_body = self.make_request(path, requestBody=values.encode('utf-8'), headers=CONTENT_TYPE_XML,
                                          method=lambda: 'POST')
        tree = etree.fromstring(response_body)
        x = tree.find('id')
        return (mms_id, identifier, x.text)


def sort_marc_tags(record):
    """sort_marc_tags(record):
    sorts the marc tags in a record in numerical order.
    Requires:
        marc_xml bib record
    Returns the sorted marc_xml bib record
    """
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
    return new_rec


def make_field(d, subfields):
    """parameter d is a dictionary carrying the values for the marc field
    parameter subfields is a list of dicts carrying the values for the subfields"""
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
    return f


def get_marc_fields(tag, bib):
    """get_marc_fields():
    retrieves all instances of a marc tag from a bib record.
    Require:
        tag - as a string (ex: '008', '020', '650')
        bib - the bibliographic record as an xml object
    returns a list of xml elements containing the marc tag
    """
    fields = bib.findall("*/[@tag='" + tag + "']")
    return fields


def has_marc_field(tag, bib):
    """has_marc_field():
    Verifies the presence of a marc field.
    Require:
        tag - as a string (ex: '008', '020', '650')
        bib - the bibliographic record as an xml object
    returns True if the tag exists, False if the tag does not exist
    """
    field = bib.find("*/[@tag='" + tag + "']")
    return type(field) == etree.Element


if __name__ == "__main__":
    # initialize sample data
    sample_limit = 10
    sample_offset = 0

    # create the service
    alma_service = Alma(use_production=False, logging=True)

    # test basic helper
    sample_mms_id = 99181224920001161
    alma_service.make_request('/bibs/test')  # smoke test to see if it's
    alma_service.make_request('/bibs/{mms_id}'.format(mms_id=sample_mms_id))

    # test real bib functionality
    sample_bib_record = alma_service.get_bib_record_by_mms_id(sample_mms_id)
    # updated_bib = alma_service.update_bib_record_by_mms_id(sample_mms_id, sample_bib)

    # holdings
    sample_holdings_id = sample_mms_id  # TODO replace with legitimate example
    holdings_delete_method = "retain"
    # holdings_list = alma_service.get_holdings_list_for_bib(sample_mms_id)
    # holdings_record = alma_service.get_holdings_record(sample_mms_id, sample_holdings_id)  # TODO resolve encoding error
    # alma_service.update_holdings_record(sample_mms_id, sample_holdings_id, holdings_record)  # TODO needs real holdings record
    # alma_service.delete_holdings_record(sample_mms_id, sample_holdings_id, holdings_delete_method)
    # alma_service.get_items_from_holdings_record(sample_mms_id, sample_holdings_id, sample_limit, sample_offset)

    # representations
    sample_rep_id = 5678  # TODO replace with legitimate example
    sample_oai_id = "arXiv.org:hep-th/9901001"
    sample_rights = "pd"
    # alma_service.get_representations_list(sample_mms_id, sample_limit, sample_offset)  # TODO resolve same encoding error
    # alma_service.get_representation(sample_mms_id, sample_rep_id)  # TODO invalid rep_id
    # alma_service.add_ia_representation(sample_mms_id, sample_oai_id, sample_rights)  # TODO unknown Bad Request (<representations total_record_count="0"/>)
    # alma_service.add_ht_representation(sample_mms_id, sample_oai_id, sample_rights)  # TODO unknown Bad Request (<representations total_record_count="0"/>)



