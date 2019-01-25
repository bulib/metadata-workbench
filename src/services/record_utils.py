from lxml import etree


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
