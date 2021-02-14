# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import tarfile
import scrapy
import packagebot.settings as settings
import os
from scrapy.pipelines.files import FilesPipeline

class PackagePipeline(object):
    def process_item(self, item, spider):
        print("Item <<<<<<<<<<<<<: %s" % item)
        return item

class PackageDownloadPipeline(FilesPipeline):

    def get_media_requests(self, item, info):        
        for file_url in item['file_urls']:
            packageName    = item['package']
            packageVersion = item['version']
            filename = "%s/%s.tar.gz" % (packageName, packageVersion)
            yield scrapy.Request(file_url, meta={'filename': filename})            
        return

    def file_path(self, request, response=None, info=None):
        return request.meta['filename']

    def item_completed(self, results, item, info):
        file_paths = ["%s/%s" % (settings.FILES_STORE, x['path']) for ok, x in results if ok]
        item['file_paths'] = file_paths        
        return item

class PackageUnzipDeletePipeline(object):
    def process_item(self, item, spider):        
        for downloadedFile in item['file_paths']:
            try:            
                print("Extracting %s" % downloadedFile)
                tar = tarfile.open(downloadedFile, "r:gz")
                tar.extractall(path=os.path.dirname(downloadedFile))
                tar.close()
            except Exception as e:
                print("Exception when extracting %s" % downloadedFile)
                print(e)
                
        return item
