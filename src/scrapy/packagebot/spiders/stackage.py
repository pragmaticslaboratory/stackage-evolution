from pickle import TRUE
import scrapy
import re
import requests
import os
from bs4 import BeautifulSoup
class PackagesSpider(scrapy.Spider):
    name = "stackage"
    files = []
    def start_requests(self):
        url =  "https://www.stackage.org/lts-"
        lts = getattr(self, 'LTS', None)
        url = url + lts
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        links = [
            y
            for y in [
                x.xpath("@href").get()
                for x in response.css("a.package-name")
            ]
            if y is not None
        ]
        #sup = len(links)
        sup = 3
        print("<<<<<<<<<< %s" % str(sup))
        for x in range(0, sup):
            next_page = links[x]
            if next_page is not None:
                next_page = response.urljoin(next_page)
                print(">>>>>>>>>>>>>> %s" % next_page)
                yield scrapy.Request(next_page, callback=self.parse_package)

    def parse_package(self, response):
        package_name = re.search(
            r".*/package/(.*)$", response.url).group(1)
        isRevissedVersion = self.settings["REVISSED"]
        if(isRevissedVersion == 'True'):
            page = requests.get("https://hackage.haskell.org/package/%s/revisions/" % package_name)
            bodyPage = BeautifulSoup(page.content, 'html.parser')
            links_versiones = ["https://hackage.haskell.org"+bodyPage.find('table').find('a', href=True)['href']]
        else:
            links_versiones = ["https://hackage.haskell.org/package/%s" % package_name]

        for next_page in links_versiones:
            print(">>>> NEXT Page: %s" % next_page)
            yield scrapy.Request(
                response.urljoin(next_page), callback=self.parse_package_version,
            )

    def parse_package_version(self, response):
        if re.search("/revision",response.url):
            typeUrl = "revision"
            package_name = re.search(r".*/package/(.*)-.*$", response.url).group(1)
            version_actual = response.url.split('/')[-1]
            package_download_url = response.url
        else:
            typeUrl = "tar"
            package_name = re.search(r".*/package/(.*)-.*$", response.url).group(1)
            version_actual = response.xpath("//th[text()='Versions ']/parent::*/td/strong/text()").get()
            package_download_url = "%s/%s-%s.tar.gz" % (
                response.url,
                package_name,
                version_actual,
            )

        yield {
            "type": typeUrl,
            "package": package_name,
            "version": version_actual,
            "package-ver": "%s-%s" % (package_name, version_actual),
            "downloadUrl": package_download_url,
            "file_urls": [package_download_url],
            "file_store": self.settings["FILES_STORE"]
        }
