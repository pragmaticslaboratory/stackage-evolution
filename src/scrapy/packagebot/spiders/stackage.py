import scrapy
import re


class PackagesSpider(scrapy.Spider):
    name = "stackage"
    start_urls = [
        "https://www.stackage.org/lts-18.18",
    ]

    files = []

    def parse(self, response):
        links = [
            y
            for y in [
                x.xpath("@href").re_first(r"(lts-18.18/package/.*)")
                for x in response.css("a.package-name")
            ]
            if y is not None
        ]
        sup = len(links)
        # sup = 3
        print("<<<<<<<<<< %s" % str(sup))
        for x in range(0, sup):
            next_page = links[x]
            if next_page is not None:
                next_page = response.urljoin(next_page)
                print(">>>>>>>>>>>>>> %s" % next_page)
                yield scrapy.Request(next_page, callback=self.parse_package)

    def parse_package(self, response):
        package_name = re.search(
            r".*lts-18.18/package/(.*)$", response.url).group(1)
        links_versiones = [
            "https://hackage.haskell.org/package/%s" % package_name]

        for next_page in links_versiones:
            print(">>>> NEXT Page: %s" % next_page)
            yield scrapy.Request(
                response.urljoin(next_page), callback=self.parse_package_version
            )

    def parse_package_version(self, response):
        package_name = re.search(r".*/package/(.*)-.*$", response.url).group(1)
        version_actual = response.xpath(
            "//th[text()='Versions ']/parent::*/td/strong/text()"
        ).get()
        package_download_url = "%s/%s-%s.tar.gz" % (
            response.url,
            package_name,
            version_actual,
        )

        dependencias_nombres = response.xpath(
            "//th[text()='Dependencies']/parent::*/td/a/text()"
        ).extract()
        dependencias_restricciones = response.xpath(
            "//th[text()='Dependencies']/parent::*/td/text()"
        ).extract()
        dependencias = zip(dependencias_nombres, dependencias_restricciones)
        Stability = response.xpath(
            "//th[text()='Stability']/parent::*/td/text()"
        ).extract()
        Category = response.xpath(
            "//th[text()='Category']/parent::*/td/a/text()"
        ).extract()
        Source_repository = response.xpath(
            "//th[text()='Source repository']/parent::*/td/a/text()"
        ).extract()
        Uploaded_by = response.xpath(
            "//th[text()='Uploaded']/parent::*/td/a/text()"
        ).extract()
        Fecha = response.xpath(
            "//th[text()='Uploaded']/parent::*/td/text()").extract()
        Uploaded_fecha = Fecha[0][0:28]

        yield {
            "package": package_name,
            "version": version_actual,
            "package-ver": "%s-%s" % (package_name, version_actual),
            "dependencias": dependencias,
            "Stability": Stability,
            "Category": Category,
            "Source_repository": Source_repository,
            "Uploaded_by": Uploaded_by,
            "Uploaded_fecha": Uploaded_fecha,
            "downloadUrl": package_download_url,
            "file_urls": [package_download_url],
        }
