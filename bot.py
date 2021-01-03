from typing import Counter
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

TIME = 0

class KickStarterBot:
    def __init__(self):
        self.driver = webdriver.Edge(executable_path="edgedriver_win64\\msedgedriver.exe")
        self.page = 1
        self.title = None
        self.author_name = None
        self.project_launch_date = None
        self.project_successfull_date = None
        self.project_fund = None
        self.project_location = None
        self.category = None
        self.location = None
        self.raised = None
        self.goal = None
        self.backers = None
        self.project_status = 'inprogress'
        self.discover()

    def discover(self):
        """
        Finding each project link from the discover page.
        """

        links = []
        self.driver.get("https://www.kickstarter.com/discover/advanced?woe_id=0&sort=magic&ref=discovery_overlay&seed=2682539&page={}".format(self.page))
        time.sleep(TIME+4)
        current_page_links = self.driver.find_elements_by_xpath("//div[@class='clamp-5 navy-500 mb3 hover-target']/a")

        for each in current_page_links:
            links.append(each.get_attribute("href"))

        while(len(links) > 0):
            current_link = links[0]
            self.parse(current_link)
            links.remove(current_link)

        self.page+=1
        self.discover()

    def parse_community_section(self, link):
        """
        Parse the author name
        """
        self.author_name = ''
        self.driver.find_element_by_xpath("//*[@id='community-emoji']").click() # Go to Community tab
        time.sleep(TIME+3)
        sentence_with_name = self.driver.find_element_by_xpath('//div[@class="title"]').text
        name_tuple = sentence_with_name.split(' ')[4:]
        self.author_name = ' '.join(name_tuple)

        if(self.author_name == None):
            self.parse_community_section(link)

        return self.author_name

    def parse_update_section(self, link):
        """
        Parse the update section
        Parse Project launch date, Project fund and Project funds successfully date
        """

        self.driver.find_element_by_xpath("//*[@id='updates-emoji']").click() # Go to Updates section
        time.sleep(TIME+3)
        
        all_divs_in_current_page = self.driver.find_elements_by_tag_name('div')
        for index, each in enumerate(all_divs_in_current_page):
            if(each.text=="Project launches"):
                self.project_launch_date = all_divs_in_current_page[index+1].text
            elif(each.text=="Project funds successfully"):
                self.project_fund = all_divs_in_current_page[index+1].text.split('$')[-1:]
                self.project_successfull_date = all_divs_in_current_page[index+2].text
                self.project_status = "successfull"                

        if(self.project_launch_date == None):
            self.parse_update_section(link)

        return (self.project_launch_date, self.project_fund, self.project_successfull_date)

    def parse_title(self, link):
        """
        Parse project title
        """
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        self.title = soup.find_all('h2')[0].text

        return self.title
    
    def parse_project_loc_cat(self, link):
        """
            Parse project location and category
        """

        tag_bar = self.driver.find_elements_by_xpath("//div[@class='py2 py3-lg flex items-center auto-scroll-x']")[0]
        tags = tag_bar.text.split('\n')

        if(tags[0] == "Project We Love"):
            self.category = tags[1]
            self.location = tags[2]
        else:
            self.category = tags[0]
            self.location = tags[1]

        if(self.category == None and self.location == None):
            self.parse_project_loc_cat(link)

        return (self.location, self.category)

    def go_to_project(self, link):
        """
        Go to a project page
        """
        self.driver.get(link)
        time.sleep(TIME + 4)

    def goal_and_raised_backers(self, link):
        """
        Parse goal, raised and backers
        """
        raised_item = self.driver.find_elements_by_xpath('//span[@class="ksr-green-500"]')[0].text
        self.raised = raised_item.split(' ')[1]
        goal_item = self.driver.find_elements_by_xpath("//span[@class='block dark-grey-500 type-12 type-14-md lh3-lg']")[0].text
        self.goal = goal_item.split(' ')[3]
        self.backers = self.driver.find_elements_by_xpath('//div[@class="block type-16 type-28-md bold dark-grey-500"]/span')[0].text

        return (self.goal, self.raised, self.backers)
        
    def parse(self, link):
        """
        Parsing for details. 
        """
        self.go_to_project(link)
        #self.parse_title(link)
        #self.parse_update_section(link)
        #self.parse_community_section(link)
        #self.parse_project_loc_cat(link)
        self.goal_and_raised_backers(link)

        payload = {
            'url': link,
            'title': self.title,
            'auther': self.author_name,
            'launched': self.project_launch_date,
            'successfull_date': self.project_successfull_date,
            'fund': self.project_fund,
            'status': self.project_status,
            'location': self.project_location,
            'category': self.category,
            'location': self.location,
            'goal': self.goal,
            'raised': self.raised,
            'backers': self.backers
        }
        print(payload)


if __name__ == '__main__':
    KickStarterBot()