import io
import re
from concurrent.futures import process
from time import sleep

from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

import scrapy
from scrapy import signals
from scrapy.packagebot.spiders import PackagesSpider

lts_list = [
    "0-7",
    "2-22",
    "3-22",
    "6-35",
    "7-24",
    "9-21",
    "11-22",
    "12-14",
    "12-26",
    "13-11",
    "13-19",
    "14-27",
    "15-3",
    "16-11",
    "16-31",
    "17-2",
    "18-6",
    "18-8",
    "18-18",
]
lts_list_wdot = [lts.replace("-", ".") for lts in lts_list]
file_store = "C:/Users/nicol/Desktop/test/lts-0-7"

result = None


def set_result(item):
    result = item


for indice, lts in enumerate(lts_list):
    print(
        "--------------------------------------------------------------------------------------------"
    )
    print(
        "---------------------------------Start with the lts",
        lts,
        "----------------------------------",
    )
    print(
        "--------------------------------------------------------------------------------------------"
    )
    file2 = io.open(
        "C:/Users/nicol/Documents/GitHub/src/scrapy/packagebot/spiders/stackage.py",
        "r",
        encoding="utf-8",
    )

    stackage = file2.readlines()

    if re.search("FILES_STORE", file_store):
        split_lts = file_store.split("-")
        direct_lts = split_lts[0] + "-" + lts + '"\n'
        file_store = direct_lts

    for idx, line in enumerate(stackage):
        if re.search("lts-", line):
            for jdx, ltswdot in enumerate(lts_list_wdot):
                if re.search(ltswdot, line):
                    stackage[idx] = stackage[idx].replace(
                        ltswdot, lts_list_wdot[indice]
                    )

    file2.close()

    listToStr1 = "".join([str(elem) for elem in stackage])
    file = io.open(
        "C:/Users/nicol/Documents/GitHub/src/scrapy/packagebot/spiders/stackage.py",
        "w",
        encoding="utf-8",
    )
    file.write(listToStr1)
    file.close()

    settings = get_project_settings()  # settings not required if running
    process = CrawlerProcess(settings)  # from script, defaults provided
    process.settings.set("FILES_STORE", 10, priority="cmdline")
    _crawl(None, PackagesSpider)
    process.start()

    print(
        "--------------------------------------------------------------------------------------------"
    )
    print(
        "---------------------------------Finish with the lts",
        lts,
        "----------------------------------",
    )
    print(
        "--------------------------------------------------------------------------------------------"
    )
