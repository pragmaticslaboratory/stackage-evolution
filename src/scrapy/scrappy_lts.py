from subprocess import call
import os
lts_list = ['2-22']
#lts_list=['0-7', '2-22', '3-22', '6-35', '7-24', '9-21', '11-22', '12-14', '12-26', '13-11','13-19', '14-27', '15-3', '16-11', '16-31', '17-2', '18-6', '18-8', '18-28', '19-11']


for lts in lts_list:
    path = os.path.join(os.path.dirname(__file__),"..\\..\\..\\..\\lts_downloaded\\tar_package")
    lts_dots = lts.replace("-",".")
    path = path+"/lts-"+lts
    comand = 'scrapy crawl stackage -s LTS="%s" -s FILES_STORE="%s" -s start_url="https://www.stackage.org/lts-%s"' % (lts_dots, path,lts_dots)
    print(comand)
    call(comand)