"""
## classes and functions for working with Alma Electronics API
## CREATED: aidans (atla5) 2019-04-05
"""

from src.services import Service, CONTENT_TYPE_XML, get_api_key

from lxml import etree


class AlmaElectronic(Service):
    """set of tools for adding and manipulating Alma ELECTRONIC bib records"""

    def __init__(self, use_production=False, logging=True):
        super(AlmaElectronic, self).__init__(use_production, logging)  # properly subclass from Service
        self.base_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
        self.api_key = get_api_key("alma", "electronic", self.env)

    def get_electronic_portfolio(self, collection_id, service_id, portfolio_id):
        path = '/electronic/e-collections/{cid}/e-services/{sid}/portfolios/{pid}'.format(
            cid=collection_id, sid=service_id, pid=portfolio_id
        )
        response = self.make_request(path, headers=CONTENT_TYPE_XML)
        return response.encode('utf-8')

    def update_electronic_portfolio(self, collection_id, service_id, portfolio_id, portfolio_obj):
        path = '/electronic/e-collections/{cid}/e-services/{sid}/portfolios/{pid}'.format(
            cid=collection_id, sid=service_id, pid=portfolio_id
        )
        portfolio_xml_string = etree.tostring(portfolio_obj, encoding='utf-8')
        response = self.make_request(
            path, method='PUT', headers=CONTENT_TYPE_XML,
            requestBody=portfolio_xml_string, return_whole_response=True
        )

        # return Boolean for whether the response is present (not None)
        return response is not None and response.status is not None


if __name__ == "__main__":
    alma_electronic_service = AlmaElectronic(use_production=True)
    collection_id = '61868923360001161'
    service_id = '62868923350001161'
    portfolio_id = '53919679890001161'
    portfolio = alma_electronic_service.get_electronic_portfolio(collection_id, service_id, portfolio_id)
    worked = alma_electronic_service.update_electronic_portfolio(collection_id, service_id, portfolio_id, etree.fromstring(portfolio))
    msg = "SUCCESS" if worked else "FAILED"
    alma_electronic_service.log_message(msg)
