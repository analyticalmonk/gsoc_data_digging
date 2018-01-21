# Issues encountered:
# -> Non-english characters
# -> issues with strings and char encoding while printing and writing to file
# -> newlines in windows for csv

import csv
import re
import time
import urllib3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from bs4 import BeautifulSoup
from lxml import html


###########################################################################
## Disable SSL verification related warnings

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
###########################################################################

## Open the two csv files in write mode
f = open('gsoc_data.csv', 'w')
gsoc_data_csv = csv.writer(f, lineterminator='\n')
gsoc_data_csv.writerow(["YEAR", "ORG_ID", "ORG_NAME", "PROJECT_NAME", "STUDENT/PROJECT URL", "MENTOR/ORG_URL"])

# g = open('org_num_selections.csv', 'w')
# num_selections_csv = csv.writer(g, lineterminator='\n')
# num_selections_csv.writerow(["year", "org_id", "org_name", "num_selections"])

###########################################################################
# 2005 - > 2008
# using lxml here

base_url = "https://developers.google.com/open-source/gsoc/"
year_list = [i for i in range(2005, 2009)]  # till 2008 works fine

## Information for different years are obtained from different webpages. Thus,
## we iterate over the year list, with each year corresponding to a distinct
## webpage.
for year in year_list:
    ## We get the relevant webpage and parse it.
    print(time.strftime("%Y-%m-%d %H:%M:%S") +" - Fetching details for year : " + str(year))
    target_url = base_url + str(year)
    target_page = requests.get(target_url)
    tree = html.fromstring(target_page.content)

    ## tree now contains the whole HTML file in a nice tree structure which we
    ## can go through using XPath.
    ## We obtain organization details, namely gsoc_id and name.
    org_list = tree.xpath('//section[@class="toc"]/ul/li/a/text()')
    org_ids = tree.xpath('//section[@class="toc"]/ul/li/a/@href')
    for num in range(len(org_ids)):
        org_ids[num] = re.sub('#', '', org_ids[num])

    ## Initialize empty lists which are to be used later.
    org_tally = []
    # project_list = []
    student_list = []
    mentor_list = []

    ## Obtain information from one organization at a time.
    for num in range(len(org_ids)):
        # print org_list[num]

        ## This gives back a list of GSoC projects for this particular org.
        projects = tree.xpath('//section[@id="%s"]/ul/li/h4/text()' % org_ids[num])
        org_tally.append(len(projects))
        # print projects
        # project_list.extend(projects)

        ## Fields in the org_numbers csv
        ## year | org_id | org_name | num_selections
        # TODO:uncomment this
        # num_selections_csv.writerow([str(year), org_ids[num], org_list[num], str(org_tally[num])])

        ## This gives back a list. Each list consists of text containing
        ## multiple lines. One line among them contains information about
        ## the mentor(s) and the student.
        participants_info = tree.xpath('//section[@id="%s"]/ul/li/text()' % org_ids[num])
        proj_counter = 0
        for line in participants_info:
            # student = re.findall('by ([\-A-Za-z\s]+),', line)
            # mentor = re.findall('mentored by ([\-A-Za-z\s]+)\n', line)
            student = re.findall('by (.+),', line)
            mentor = re.findall('mentored by (.+)\n', line)
            if len(student) == 1 or len(mentor) == 1:
                student_list.extend(student)
                mentor_list.extend(mentor)
                ## Fields in the proj_details csv
                ## year | org_id | org_name | project_name | student | mentor
                gsoc_data_csv.writerow([str(year),
                                        org_ids[num],
                                        org_list[num],
                                        str(projects[proj_counter]),
                                        str(student[0]),
                                        str(mentor[0])
                                        ])
                proj_counter += 1
    print("Done")
    time.sleep(5)

###########################################################################
# 2009 -> 2015
# use beutifulsoup here
year_list = [i for i in range(2009, 2016)]  # till 2015 works fine
ybase_url = "https://www.google-melange.com"  # +year

# eg link  -> https://www.google-melange.com/archive/gsoc/2009/orgs/atheme/
for year in year_list:
    print(time.strftime("%Y-%m-%d %H:%M:%S")+ " - Fetching details for year : " + str(year))
    y_url = ybase_url + "/archive/gsoc/" + str(year)

    r = requests.get(y_url, verify=False)
    soup = BeautifulSoup(r.text, 'lxml')
    ul = soup.find("ul", {"class": "mdl-list"})
    li_set = ul.findAll("li")

    for li in li_set:
        a = li.find("a")
        org_name = a.text
        org_link = str(a.attrs['href'])
        org_id = org_link.split("/")[-1]
        org_url = ybase_url + org_link
        # print(org)
        r = requests.get(org_url, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')
        ul = soup.find("ul", {"class": "mdl-list"})
        li_set_p = ul.findAll("li")

        try:
            for p in soup.findAll("p"):
                if "Web Page:" in p.text:
                    org_web_url = p.find("a").attrs['href']  # second containing webpage keyword
                    break
        except AttributeError:
            print("proj_web_url: exception for -> " + org_id)  # freifunk 2009 openwrt exception
            org_web_url = ""
        for li_p in li_set_p:
            a_p = li_p.find("a")
            proj_name = a_p.text
            proj_link = str(a_p.attrs['href'])
            proj_url = ybase_url + proj_link

            gsoc_data_csv.writerow([str(year),
                                    org_id,
                                    org_name,
                                    str(proj_name),
                                    proj_url,
                                    str(org_web_url)
                                    ])
            # print([str(year),
            #        org_id,
            #        org_name,
            #        str(proj_name),
            #        proj_url,
            #        str(org_web_url)
            #        ])
            time.sleep(0.1)  # google might block because of too many requests
    print("Done")
    time.sleep(5)

###########################################################################
# 2016 -> 2017
year_list = [i for i in range(2016, 2018)]  # till 2015 works fine
base_url = "https://summerofcode.withgoogle.com/archive/2016/projects/?page="

max_pages = 15
for year in year_list:
    print(time.strftime("%Y-%m-%d %H:%M:%S")+" - Fetching details for year : " + str(year))
    for i in range(1, max_pages):
        print("page -> " + str(i))
        url = base_url + str(i)
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            section = soup.find("section", attrs={"class", "lifted-section"})
            a_set = section.findAll("a")
        except AttributeError:
            continue
        # print("nextlink ->"+ a_set[-1].attrs["href"])
        if i > 1:
            k = 2  # for previous and next
        else:
            k = 1  # for next button next

        for j in range(len(a_set) - k):  # last link is next
            proj_link = a_set[j].attrs["href"]
            proj_url = "https://summerofcode.withgoogle.com" + str(proj_link)
            r = requests.get(proj_url, verify=False)
            soup = BeautifulSoup(r.text, 'lxml')
            try:
                proj_name = ""
                proj_name = soup.find("h3").text
                meta_div = soup.find("div", attrs={"class", "org__meta"})
                get_code_link = meta_div.findAll("a")[0].attrs["href"]
                code_url = str(get_code_link)
                org_name = meta_div.findAll("a")[1].text
                org_web_link = meta_div.findAll("a")[1].attrs["href"]
                org_web_url = "https://summerofcode.withgoogle.com" + org_web_link
                org_id = ""

                gsoc_data_csv.writerow([str(year),
                                        org_id,
                                        org_name,
                                        str(proj_name),
                                        code_url,
                                        str(org_web_url)
                                        ])
                # print([str(year),
                #        org_id,
                #        org_name,
                #        str(proj_name),
                #        code_url,
                #        str(org_web_url)
                #        ])
            except AttributeError:
                print("exception for -> ", proj_url)
            time.sleep(0.1)

    print("Done")
    time.sleep(5)
###########################################################################
f.close()
# g.close()
