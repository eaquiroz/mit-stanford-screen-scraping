from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

from scrapy.contrib.spiders import CrawlSpider
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from scrapy.contrib.linkextractors import LinkExtractor

from stanford.items import StanfordItem

class StanfodSpider(CrawlSpider):
    name = 'stanford'
    login_url = "https://alumni.stanford.edu/get/page/directory/advanced/"
    start_urls = ["https://alumni.stanford.edu/get/page/directory/advanced/"]

    def start_requests(self): 
        # This method is called first, by default.
        return [Request(url=self.login_url,
                       callback=self.login,
                       dont_filter=True)]

    def login(self, response):
        # Generate a login request.
        return FormRequest.from_response(response, formname='mainform',
                    formdata={'username': 'bryanfinkel', 'password': 'GretaStan99'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        # Check the response returned by a login request to see if we are successfully logged in.
        if "Log Out" in response.body:
            self.log("\n\n\nSuccessfully logged in. Let's start crawling!\n\n\n")
            # Go to search page
            return self.search(response)

        else:
            self.log("\n\n\nFailed login.\n\n\n")
            # Something went wrong, we couldn't log in, so nothing happens.

    def search(self, response):
        # Fill in form (search field) with default term "data scientist" and search.
        if "Advanced Search" in response.body:
            self.log("\n\n\n Made it to the search! \n\n\n")
            return FormRequest.from_response(response,
                # Default term will be changed later...currently using "data scientist" for testing purposes.
                    formdata={'employment_title': 'data scientist'},
                    callback=self.parse_results)
        else:
            self.log("\n\n\n Didn't make it to the search. \n\n\n")

    def parse_results(self, response):
        if "Anish" in response.body:
            self.log("\n\n yay! \n\n")
        else:
            self.log("\n\n no \n\n")
        for result in response.xpath('//tr[@class="first"]/h5/a'):
            item = StanfordItem()
            # Add name fields to item
            name_line = result.xpath('normalize-space(span/text())').extract()
            item['name'] = name_line
            # Get company and job title fields
            # Step in one page (click on result name) and parse result page
            # links = result.xpath('@href').extract()
            # if links:
            #     self.log("\n\n Stepped in a page. \n\n")
            #     result_page = "https://alumni.stanford.edu" + links[0]
            #     request = Request(url=result_page,
            #                   callback=self.parse_result_page)
            #     request.meta['item'] = item
            #     yield request
            # Yield completed item
            # else:
            #     yield item

        link_elements = response.xpath('//div[@class="clearfix paginationContainer"]/div[@class="floatright"]/a').extract()
        for link_element in link_elements:
            if "next" in link_element.xpath('text()').extract():
                next_page = link_element.xpath('@href')
                yield Request(url=next_page,
                              callback=self.parse_results)
            

    def parse_result_page(self, response):
        self.log("\n\n Parsing result page. \n\n")
        item = response.meta['item']
        # Get home address and work address fields
        print(response.xpath('//div[@id="content"]').extract())
        if response.xpath('//li[@class="homeAddress"]').extract():
            home_address = response.xpath('//li[@class="homeAddress"]/strong/following-sibling::text()').extract()
            item['home_address'] = home_address
        if response.xpath('//ul/li[@class="workAddress"]').extract():
            work_address = response.xpath('//ul/li[@class="workAddress"]/strong/following-sibling::text()').extract()
            item['work_address'] = work_address
        # Get phone and email fields
        for line in response.xpath('//div[@class=content]/ul/li').extract():
            if "Email:" in line.xpath('strong/text()').extract():
                    item['email'] = line.xpath('normalize-space(strong/following-sibling::text())').extract()
                    # return item
                    return item
        return item

