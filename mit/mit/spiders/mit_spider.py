from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

from scrapy.contrib.spiders import CrawlSpider
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from scrapy.contrib.linkextractors import LinkExtractor

from mit.items import MitItem

class MitSpider(CrawlSpider):
    name = 'mit'
    login_url = "https://alum.mit.edu/user/directory/home.dyn"
    start_urls = ["https://alum.mit.edu/user/directory/home.dyn"]

    def start_requests(self): 
        # This method is called first, by default.
        return [Request(url=self.login_url,
                       callback=self.login,
                       dont_filter=True)]

    def login(self, response):
        # Generate a login request.
        return FormRequest.from_response(response, formname='mainform',
                    formdata={'username': 'bfinkel', 'password': 'Greta99'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        # Check the response returned by a login request to see if we are successfully logged in.
        if "Logout" in response.body:
            self.log("\n\n\nSuccessfully logged in. Let's start crawling!\n\n\n")
            # Go to search page
            return self.search(response)

        else:
            self.log("\n\n\nFailed login.\n\n\n")
            # Something went wrong, we couldn't log in, so nothing happens.

    def search(self, response):
        # Fill in form (search field) with default term "data scientist" and search.
        if "Start your search by using the search box or categories on the left." in response.body:
            self.log("\n\n\n Made it to the search! \n\n\n")
            return FormRequest.from_response(response,
                # Default term will be changed later...currently using "data scientist" for testing purposes.
                    formdata={'newNtt': 'data scientist'},
                    callback=self.parse_results)
        else:
            self.log("\n\n\n Didn't make it to the search. \n\n\n")

    def parse_results(self, response):
        count = 1
        for result in response.xpath('//div[@class="result"]'):
            if count <= 5:
                item = MitItem()
                # Add name fields to item
                name_line = result.xpath('normalize-space(h4/a/text())').extract()
                name = name_line[0].split("\'")[0].split()
                item['first_name'] = name[1]
                item['last_name'] = name[0][:-1]
                # Get company and job title fields
                for line in result.xpath('ul/li'):
                    if "Company:" in line.xpath('strong/text()').extract():
                        item['company'] = line.xpath('normalize-space(strong/following-sibling::text())').extract()
                    elif "Job Title:" in line.xpath('strong/text()').extract():
                        item['job_title'] = line.xpath('normalize-space(strong/following-sibling::text())').extract()
                # Step in one page (click on result name) and parse result page
                links = result.xpath('h4/a/@href').extract()
                if links:
                    result_page = "https://alum.mit.edu" + links[0]
                    request = Request(url=result_page,
                                  callback=self.parse_result_page)
                    request.meta['item'] = item
                    yield request
                # Yield completed item
                else:
                    yield item
                count += 1

        # Recursively crawl the "next page" - currenty commented out to minimize records accessed       
        # links = response.xpath('//div[@class="clearfix"]/div/ul/li[@id="next-page"]/a/@href').extract()
        # if links:
        #     next_page = "https://alum.mit.edu" + links[0]
        #     yield Request(url=next_page,
        #                   callback=self.parse_results)

    def parse_result_page(self, response):
        item = response.meta['item']
        # Get home address and work address fields
        if response.xpath('//ul/li[@class="homeAddress"]').extract():
            split_home_address = " ".join(response.xpath('//ul/li[@class="homeAddress"]/strong/following-sibling::text()').extract()).split()
            home_address = " ".join(split_home_address)
            item['home_address'] = home_address
        if response.xpath('//ul/li[@class="workAddress"]').extract():
            split_work_address = " ".join(response.xpath('//ul/li[@class="workAddress"]/strong/following-sibling::text()').extract()).split()
            work_address = " ".join(split_work_address)
            item['work_address'] = work_address
        # Get email field
        for line in response.xpath('//ul/li'):
            if "Email:" in " ".join(line.xpath('strong/text()').extract()):
                item['email'] = line.xpath('normalize-space(a/text())').extract()
                return item
        return item

