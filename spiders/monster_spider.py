import scrapy
import json
from ..items import MonsterItem
import time
from bs4.element import Comment
import re,random
from bs4 import BeautifulSoup


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


jobtitle = input("Please enter the job title you want to crawl \n"
                     "(word separated by '-', e.g. web-developer) :")
pages = input("Please enter the number of pages you want to crawl :")


class MonsterSpider(scrapy.Spider):

    name = 'monster-spider'
    allowed_domains = ['monster.com']

    start_urls = ['https://www.monster.com/jobs/search/pagination/?q='+jobtitle+
                  '&where=usa&isDynamicPage=true&isMKPagination=true&page={}'.format(i + 1) for i in range(int(pages))]
    postingid = []


    def parse(self, response):

        results = json.loads(response.body.decode('utf-8'))
        pattern = re.compile(r'data-m_impr_j_postingid=\"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}\"')
        matches = pattern.findall(str(results))
        for match in matches:
            match = match.strip('data-m_impr_j_postingid="')
            self.postingid.append(match)
        for id in self.postingid:
            next_url = 'https://job-openings.monster.com/v2/job/pure-json-view?&jobid='+id
            #time.sleep(random.uniform(0.1, 2.2))
            yield response.follow(next_url, callback=self.parse_detail)

    def parse_detail(self, response):
        item = MonsterItem()
        result = json.loads(response.body.decode('utf-8'))

        title = result["companyInfo"]["companyHeader"]
        companyname = result["companyInfo"]["name"]
        companyurl = result["companyInfo"]["websiteUrl"]
        jobLocationRegion  = result["jobLocationRegion"]
        jobLocationCity = result["jobLocationCity"]
        jobdescription_raw = result["jobDescription"]

        #salary = str(re.findall(r"(\$\d\d\.\d\d)", str(result["applyStartTrackingAttributesJson"])))
        jobdescription = text_from_html(jobdescription_raw)



        item['title'] = title
        item['companyname'] = companyname
        item['companyurl'] = companyurl
        item['jobLocationRegion'] = jobLocationRegion
        item['jobLocationCity'] = jobLocationCity
        item['jobdescription'] = jobdescription
        #item['salary'] = salary
        return item








