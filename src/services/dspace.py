"""
## classes and functions for working with  Dspace
## jwammerman
## September 2019
"""

from urllib.request import Request, urlopen
from urllib.parse import quote_plus


class Dspace:
    '''
    a set of tools to obtain records from Dspace
    '''

    def __init__(self):
        pass
        return

    def get_openBU_results(identifier, rights):
        '''get_primo_results executes the search and returns the response'''
        url = 'http://open.bu.edu/oai/request?verb=GetRecord&identifier={{identifier}}&metadataPrefix=marc'
        url = url.replace('{{identifier}}', quote_plus(identifier))
        # print(url)
        request = Request(url)
        # rights = 0
        recno = identifier
        if type(rights) != str:
            rights = 'Undetermined'
            # rights = 'cc-by-nc-sa-4.0'
        rights_dict = {'pd': 'public domain', 'pdus': 'public domain (US)', 'icworld': 'in copyright (world)',
                       'icus': 'in copyright (US)', 'ic': 'in copyright', 'und': 'unknown',
                       'cc-by-nc-nd-3.0': 'Creative Commons Attribution-NonCommercial-NoDerivatives',
                       'cc-by-nc-nd-4.0': 'Creative Commons Attribution-NonCommercial-NoDerivatives',
                       'cc-by-nc-3.0': 'Creative Commons Attribution-NonCommercial',
                       'cc-by-nc-4.0': 'Creative Commons Attribution-NonCommercial',
                       'cc-by-nc-sa-4.0': 'Creative Commons Attribution-NonCommercial-ShareAlike',
                       'cc-by-nc-sa-3.0': 'Creative Commons Attribution-NonCommercial-ShareAlike',
                       'cc-by-sa-4.0': 'Creative Commons Attribution-ShareAlike',
                       'cc-by-sa-3.0': 'Creative Commons Attribution-ShareAlike',
                       'cc-by-3.0': 'Creative Commons Attribution',
                       'cc-by-4.0': 'Creative Commons Attribution',
                       }

        ## now let's add the ht_recno to 024$a
        if rights in rights_dict:
            rights = rights_dict[rights]

        _024 = '''       <datafield ind1="7" ind2=" " tag="024">
                <subfield code="a">{{OpenBU_record}}</subfield>
                <subfield code="c">{{rights}}</subfield>
                <subfield code="2">OpenBU</subfield>
                <subfield code="0">http://hdl.handle.net/{{record}}</subfield>
            </datafield>'''.replace('{{OpenBU_record}}', recno).replace('{{rights}}', rights).replace('{{record}}',
                                                                                                      recno[16:])
        _924 = '''       <datafield ind1="7" ind2=" " tag="924">
                <subfield code="a">{{OpenBU_record}}</subfield>
                <subfield code="c">{{rights}}</subfield>
                <subfield code="2">OpenBU</subfield>
                <subfield code="0">http://hdl.handle.net/{{record}}</subfield>
            </datafield>'''.replace('{{OpenBU_record}}', recno).replace('{{rights}}', rights).replace('{{record}}',
                                                                                                      recno[16:])

        field_924 = ET.fromstring(_924)
        field_024 = ET.fromstring(_024)

        try:

            response_body = urlopen(request).read()
            oai_result = ET.fromstring(response_body)
            # ns = {'oai':'http://www.openarchives.org/OAI/2.0/','marc':'http://www.loc.gov/MARC21/slim'}

            ns = {'oai': 'http://www.openarchives.org/OAI/2.0/', 'marc': 'http://www.loc.gov/MARC21/slim',
                  'ns0': 'http://www.openarchives.org/OAI/2.0/'}
            header = oai_result.find('./ns0:GetRecord/ns0:record/ns0:header', ns)
            try:
                if header.attrib['status'] == 'deleted':
                    return ('deleted', '')
            except Exception as e:
                pass

            oai_header = oai_result.find('oai:GetRecord', ns).getchildren()[0][0]
            metadata = oai_result.find('oai:GetRecord', ns).getchildren()[0][1]
            marc_record = metadata.find('marc:record', ns)
            _024s = marc_record.findall('*/[@tag="024"]')
            for _024 in _024s:
                marc_record.remove(_024)
            marc_record.append(field_024)
            marc_record.append(field_924)

            for el in marc_record.findall('*/[@tag="720"]'):
                for e in el.getchildren():
                    # print(e.tag,e.attrib,e.text)
                    if e.text == 'author':
                        el.attrib = {'tag': '100', 'ind1': '1', 'ind2': ' '}

            # marc_record = sort_marc_tags(marc_record)
        except Exception as e:
            print('There was an exception')
            print(e)
            oai_header = ''
            marc_record = ''
        # print(ET.tostring(marc_record))
        return (oai_header, marc_record)

