from gspread import client
from selenium import webdriver
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import time
import gspread


# Add additional delay to the TIME variable if your internet speed is low. 
TIME = 0

# Download the credentials file from google cloud and save to current directory.
# How to create credentials file? 
# Create a new project on Google Cloud.
# Give accesss to Google Drive API and Google Spreadsheets API.
# Share client_mail in credentials with the Google Sheet you want to write to.

#SETUP
CREDENTIALS_FILE_NAME = 'credentials.json'
SHEET_NAME = 'kickstarter-bot'
EXECUTABLE_PATH = 'edgedriver_win64//msedgedriver.exe'

class KickStarterBot:
    def __init__(self):
        self.driver = webdriver.Edge(executable_path=EXECUTABLE_PATH)
        self.count = 0
        self.page = 1
        self.title = None
        self.author_name = None
        self.project_launch_date = None
        self.project_successfull_date = None
        self.project_successfull_fund = None
        self.category = None
        self.location = None
        self.raised = None
        self.goal = None
        self.backers = None
        self.project_status = 'inprogress'
        self.spreadsheet_setup()
        self.discover()

        
    def spreadsheet_setup(self):
        scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive'
                ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_NAME , scope)
        client = gspread.authorize(credentials)
        self.sheet = client.open(SHEET_NAME).sheet1


    def discover(self):
        """
        Finding each project link from the discover page.
        """

        links = []
        self.driver.get("https://www.kickstarter.com/discover/advanced?woe_id=0&sort=magic&ref=discovery_overlay&seed=2682539&page={}".format(self.page))
        time.sleep(TIME+4)
        if(self.driver.title != "The page you were looking for doesn't exist (404)"):
            current_page_links = self.driver.find_elements_by_xpath("//div[@class='clamp-5 navy-500 mb3 hover-target']/a")

            for each in current_page_links:
                links.append(each.get_attribute("href"))

            while(len(links) > 0):
                current_link = links[0]
                self.count += 1
                self.parse(current_link)
                links.remove(current_link)

            self.page+=1
            self.discover()
        else:
            print("You have ${self.count} of project data in your database :)")

    def parse_community_section(self, link):
        """
        Parse the author name
        """

        try:
            self.driver.find_element_by_xpath("//*[@id='community-emoji']").click() # Go to Community tab
            time.sleep(TIME+3)
            sentence_with_name = self.driver.find_element_by_xpath('//div[@class="title"]').text
            name_tuple = sentence_with_name.split(' ')[4:]
            self.author_name = ' '.join(name_tuple)
        except:
            print("parse_community_section exception.")

            if(self.author_name == None):
                time.sleep(1)
                self.parse_community_section(link)

        return self.author_name

    def parse_update_section(self, link):
        """
        Parse the update section
        Parse Project launch date, Project fund and Project funds successfully date
        """
        try:
            no_updates = self.driver.find_element_by_xpath("//*[@id='project-post-interface']/div/h3").text
            if(type(no_updates)==str):
                print("no_update_page_reload_yes")
                self.parse(link)
            else:
                print("no_update_page_reload_no")
        except:
            try:
                self.driver.find_element_by_xpath("//*[@id='updates-emoji']").click() # Go to Updates section
                time.sleep(TIME+2)
                
                all_divs_in_current_page = self.driver.find_elements_by_tag_name('div')
                for index, each in enumerate(all_divs_in_current_page):
                    if(each.text=="Project launches"):
                        self.project_launch_date = all_divs_in_current_page[index+1].text
                    if(each.text=="Project funds successfully"):
                        self.project_successfull_fund = all_divs_in_current_page[index+1].text.split('$')[-1:]
                        self.project_successfull_date = all_divs_in_current_page[index+2].text
                        self.project_status = "successfull"                
            except:
                print("parse_update_section exception.")

        if(self.project_launch_date == None):
            time.sleep(1)
            self.parse_update_section(link)

        return (self.project_launch_date, self.project_successfull_fund, self.project_successfull_date)

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
        
        try:
            raised_item = self.driver.find_elements_by_xpath('//span[@class="ksr-green-500"]')[0].text
            self.raised = raised_item.split('$')[1]
        except IndexError:
            print(link)
            print("goal_and_raised_backers__raised_exception.")
        except:
            print("goal_and_raised_backers__raised_exception.")
            
        try:
            goal_item = self.driver.find_elements_by_xpath("//span[@class='block dark-grey-500 type-12 type-14-md lh3-lg']")[0].text
            self.goal = goal_item.split(' ')[3]
            self.backers = self.driver.find_elements_by_xpath('//div[@class="block type-16 type-28-md bold dark-grey-500"]/span')[0].text            

            if(self.goal!=None and self.goal=="goal"):
                self.goal = goal_item.split(' ')[2]
            if(self.goal!=None and self.goal[:1]!='$'):
                self.goal = '${}'.format(self.goal)
            if(self.raised!=None and self.raised[1:]!='$'):
                self.raised = '${}'.format(self.raised)
        except:
            print("goal_and_raised_backers__goal_exception.")
        
        return (self.goal, self.raised, self.backers)
        
    def print_data(self, link):
        """
        Print data to the terminal.
        """

        print("\n\nCount: ", self.count)
        print("URL: ", link)
        print("Title: ", self.title)
        print("Location: ", self.location)
        print("Category: ", self.category)
        print("Goal: ", self.goal)
        print("Raised: ", self.raised)
        print("Backers: ", self.backers)
        print("Status: ", self.project_status)
        print("Author : ", self.author_name)
        print("Launch: ", self.project_launch_date)
        if(self.project_status!="inprogress"):
            print("Project successfull Fund: ", self.project_successfull_fund)
        if(self.project_status!="inprogress"):
            print("Project Status: ", self.project_successfull_date)

        
    def save_to_sheet(self, payload):
        """
        Saving to google spreadsheets through API
        """

        content = ['Name', 'URL', 'Author', 'Launch', 'Status',
                   'Category', 'Location', 'Goal', 'Raised', 'Backers', 'Successful on',
                   'Successfully funded']
        if(self.sheet.cell(1, 1).value != "Name"):
            self.sheet.insert_row(content, 1)
        else:
            self.sheet.insert_row(payload, 2)

    def parse(self, link):
        """
        Parsing for details. 
        """
        self.go_to_project(link)
        self.parse_title(link)
        self.goal_and_raised_backers(link)
        self.parse_project_loc_cat(link)
        self.parse_update_section(link)
        self.parse_community_section(link)
        self.print_data(link)

        payload = [
            self.title,
            link,
            self.author_name,
            self.project_launch_date,
            self.project_status,
            self.category,
            self.location,
            self.goal,
            self.raised,
            self.backers,
            self.project_successfull_date,
            self.project_successfull_fund,
        ]

        self.save_to_sheet(payload)


if __name__ == '__main__':
    KickStarterBot()