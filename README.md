---

title: Scraping Job Information using Scrapy and Visualizing its Data
ate: 2019-10-30 23:20:44
tags:
---

# Overview

I intended to scrape only ***monster.com***, which is one of the best job search websites, but changed my mind when I found out most of posted jobs does not contain salary info. It's not fun at all, so I chose ***glassdoor.com*** as my second target website. In this project, I mainly focused on three jobs(Data Analyst, Web Developer and Mobile APP Developer) in monster website.

The diagram below shows the workflow of collecting structured raw data from web pages, selecting some of that data, parsing/visualizing data. 

<img src="https://i.ibb.co/Cw8wqCX/web-scrapy-1.png" alt="avatar" style="zoom: 200%;" />

<br/><br/>

# Assigning Attributes to the Spider 

After setting up the environment and creating a scrapy project, codes in the **monster_spider.py** file are as follows:

```python
class MonsterSpider(scrapy.Spider):
    name = 'monster-spider'
    allowed_domains = ['monster.com']
    start_urls = ['https://www.monster.com/jobs/search/pagination/?q='+jobtitle+
                  '&where=usa&isDynamicPage=true&isMKPagination=true&page={}'.format(i+1) for i in range(int(pages))]
    postingid = []
    def parse(self, response):
        pass
```

Usually  **start_urls** class attribute is defined as the homepage of the website where the spider will begin to crawl(e.g. https://www.monster.com/jobs/search/?q=Data-Analyst) and then be used by the default implementation of **start_requests()** to generate initial requests. Yet a URL looking like server-side web API was found when browsing through web pages by using Chrome DevTools.

<img src="https://i.ibb.co/xq586M9/2019-11-03-140231.png" alt="avatar" style="zoom: 200%;" />

It returns information in well-structured JSON format, each page contains 25-30 job positions and one of them is shown in the diagram below(edited by JSON Beautifier), which is clearer to parse than using XPath or Css selector to locate web elements. 

<img src="https://i.ibb.co/jRf7VFL/2019-11-03-144730.png" alt="avatar" style="zoom: 200%;" />

Obviously, each ~~durian~~ job is specific to a particular MusangKingId and a postingId. Both IDs work well but not all jobs have MusangKingId. Therefore a list of this URLs are assigned to **start_urls** in order to get postingId, **jobtitle** and number of **pages** are defined by user input.

<br/><br/>

# Parse()

```python
 def parse(self, response):
        results = json.loads(response.body.decode('utf-8'))
        pattern = re.compile(r'data-m_impr_j_postingid=\"\w{8}-\w{4}-\w{4}-\w{4}- 																				\w{12}\"')
        matches = pattern.findall(str(results))
        for match in matches:
            match = match.strip('data-m_impr_j_postingid="')
            self.postingid.append(match)
        for id in self.postingid:
            next_url = 'https://job-openings.monster.com/v2/job/pure-json-view&jobid='+id
            time.sleep(random.uniform(0.1, 0.5))
            
            yield response.follow(next_url, callback=self.parse_detail)
```

Postingid locating at the middle of texts of ImpressionTracking can be easily grabbed by using Regex. Similarly, **next_url**, containing detailed single job information in JSON format, was found by using DevTools. The part of data it contains, as shown in following picture, is very neat except for the tags and html comments in jobdescription part. This can be removed by using BeautifulSoup and bs4.element.

<img src="https://i.ibb.co/r5g6Th9/2019-11-03-160853.png" alt="avatar" style="zoom: 200%;" />In the last line of **parse()**, it returns a generator and **next_url**  is passed to **parse_detail()**.

<br/><br/>

# Parse_detail()

```python
    def parse_detail(self, response):
        item = MonsterItem()
        result = json.loads(response.body.decode('utf-8'))

        item['title'] = result["companyInfo"]["companyHeader"]
        item['companyname'] = result["companyInfo"]["name"]
        item['companyurl'] = result["companyInfo"]["websiteUrl"]
        item['jobLocationRegion']  = result["jobLocationRegion"]
        item['jobLocationCity'] = result["jobLocationCity"]
        item['jobdescription'] = result["jobDescription"]
        
        return item
```

Since all data are in JSON format, the code for extracting needed data is clean and simple. After this, spider returns the extracted data(python dictionary format) to containers(class MonsterItem in items.py file) 

<br/><br/>

# Storing data in SQLite3 Database

In order to export data to SQLite, we need to connect with database and create table in **pipelines.py**. An elaborate introduction about pipelines can be found in *docs.scrapy.org* :

________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

After an item has been scraped by a spider, it is sent to the Item Pipeline which processes it through several components that are executed sequentially. Each item pipeline component (sometimes referred as just “Item Pipeline”) is a Python class that implements a simple method. They receive an item and perform an action over it, also deciding if the item should continue through the pipeline or be dropped and no longer processed.

Typical uses of item pipelines are:

- cleansing HTML data
- validating scraped data (checking that the items contain certain fields)
- checking for duplicates (and dropping them)
- **storing the scraped item in a database**

________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

 ```python
class MonsterPipeline(object):
    
    def __init__(self):
        self.create_connection() 
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect("jobinfo.db")  
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS job_tb""")
        self.curr.execute("""create table job_tb(title text)""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self,item):
        self.curr.execute("""insert into job_tb values(?)""",(item['title']))
        self.conn.commit()
 ```

The block of code above is an example for storing only job title, **create_connection()** and **create_table()** are implement in the **init** function, they will do their jobs as the name implies whenever the class **MonsterPipeline()** is initialized. 

To ensure pipeline works, a block of default code shown below in **settings.py** needs to be uncomment.

```python
ITEM_PIPELINES = {
   'monster.pipelines.MonsterPipeline': 300,
}
```

After opening the generated database file in SQLite, it looks like the table below.

<img src="https://i.ibb.co/6bksvP3/2019-11-03-225027.png" alt="avatar" style="zoom: 200%;" />

<br/><br/>

# Anti-scraping Techniques 

Monster.com do not need CAPTCHA to have access to any data, so the spider only uses three anti-scraping methods, which are varying scraping speed, random User-Agent provided by scrapy*-*fake*-*useragent(https://github.com/hyan15/scrapy-proxy-pool) and rotating IP provided by scrapy-proxy-pool(https://pypi.org/project/scrapy-fake-useragent/). There are detailed information on the links for the last two libraries.

<br/><br/>

#  Glassdoor Spider

Since the site structure of glassdoor is somewhat different with monster, I built another spider based on **Scrapy** and **Urllib**. See full code on https://github.com/A3M4/Glassdoor.com-Job-Info-Web-Crawler-by-Scrapy The spider is connected with **MySQL Workbench**, its table for data analyst is shown below and the salary range that employer listed is separated into two columns: salarylow and salryhigh. Besides, the meaning of size and year are "number of employees" and "company founded year".

<img src="https://i.ibb.co/Rg5chvc/2019-11-03-230227.png" alt="avatar" style="zoom: 200%;" />

<br/><br/>

# Data Visualization

The visualizations  were created by using Tableau and Matplotlib, Tableau is a fantastic software for making nice presentation and basic analysis, but for heavy lifting, visualizing libraries in R or Python are definitely my first choice. The following image provides basic info(average base salary, star rating by employees and company founded year) for these three positions.

<img src="https://i.ibb.co/9smGWP2/basicinfo-glass.jpg" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Ranking of Most Mentioned skills for Data Analyst

<img src="https://i.ibb.co/yk5vZHJ/Download-Image.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Most Occurring Adjectives in Job Description

<img src="https://i.ibb.co/JQwhyyF/Dashboard-1-7.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Educational Requirements to Land a Job

<img src="https://i.ibb.co/xS7PJ30/Dashboard-1-5.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## What are the Sizes of Tech Companies? 

<img src="https://i.ibb.co/SV0dh9d/size.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Which City has the Most Opportunities for Data Analyst?

<img src="https://i.ibb.co/dbYzH2r/Dashboard-1-10.png" alt="avatar" style="zoom: 200%;" />

<br/><br/>

## The Relationship between Salary and Age of Firm

<img src="https://i.ibb.co/KW15P23/SALARY-YEAR.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Annual Average Salary in Each State

<img src="https://i.ibb.co/pKv5FzT/Dashboard-1-3.png" alt="avatar" style="zoom: 100%;" />

<br/><br/>

## Numbers of Years of Experience Required by Employers 

<img src="https://i.ibb.co/rdLnFpr/Dashboard-1-4.png" alt="avatar" style="zoom: 100%;" />