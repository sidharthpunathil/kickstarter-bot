from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

TIME = 0

class KickStarterBot:
    def __init__(self):
        self.driver = webdriver.Edge(executable_path="edgedriver_win64\\msedgedriver.exe")
        self.page = 1
        self.discover()

    def discover(self):
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
    
    def parse(self, link):
        self.driver.get(link)
        time.sleep(TIME+3)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        Name = soup.find_all('h2')[0].text

        payload = {
            'name': Name,
            'url': link
        }
        print(payload)

        self.driver.find_element_by_xpath("//*[@id='updates-emoji']").click() # Click Updates
        time.sleep(TIME+4)
        
        all_divs_in_current_page = self.driver.find_elements_by_tag_name('div')
        for index, each in enumerate(all_divs_in_current_page):
            if(each.text=="Created by"):
                author_name = all_divs_in_current_page[index+3].text
                print(author_name)
            if(each.text=="Project launches"):
                project_launch_date = all_divs_in_current_page[index+1].text
                print("project launch date", project_launch_date)
            elif(each.text=="Project funds successfully"):
                project_fund = all_divs_in_current_page[index+1].text.split('$')[-1:]
                project_successfull_date = all_divs_in_current_page[index+2].text
                print("successful: ", project_fund, project_successfull_date)

        launches= self.driver.find_elements_by_xpath("""div[class="type-11 type-14-sm text-uppercase"]""")
        for each in launches:
            print("inside loop")
            print(each.text)

        input()

if __name__ == '__main__':
    KickStarterBot()