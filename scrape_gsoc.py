# Issues encountered:
# -> Non-english characters
# -> issues with strings and char encoding while printing and writing to file
# -> newlines in windows for csv

import requests
import re
from lxml import html
import csv

base_url = "https://developers.google.com/open-source/gsoc/"
year_list = [2005, 2006, 2007, 2008]

## Open the two csv files in write mode
f = open('proj_details.csv', 'w')
projDetailsWriter = csv.writer(f, lineterminator='\n')
# Start by writing the header of the csv file
projDetailsWriter.writerow(["year", "org_id", "org_name", "project_name",
                            "student", "mentor"])

g = open('org_numbers.csv', 'w')
orgNumWriter = csv.writer(g, lineterminator='\n')
# Start by writing the header of the csv file
orgNumWriter.writerow(["year", "org_id", "org_name", "num_selections"])

## Information for different years are obtained from different webpages. Thus,
## we iterate over the year list, with each year corresponding to a distinct
## webpage.
for year in year_list:
    ## We get the relevant webpage and parse it.
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
        projects = tree.xpath('//section[@id="%s"]/ul/li/h4/text()' %
                              org_ids[num])
        org_tally.append(len(projects))
        # print projects
        # project_list.extend(projects)

        ## Fields in the org_numbers csv
        ## year | org_id | org_name | num_selections
        orgNumWriter.writerow([str(year), org_ids[num], org_list[num],
                               str(org_tally[num])])

        ## This gives back a list. Each list consists of text containing
        ## multiple lines. One line among them contains information about
        ## the mentor(s) and the student.
        participants_info = tree.xpath('//section[@id="%s"]/ul/li/text()' %
                                       org_ids[num])
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
                projDetailsWriter.writerow([str(year), org_ids[num],
                                            org_list[num],
                                            projects[proj_counter].encode('utf8'),
                                            student[0].encode('utf8'),
                                            mentor[0].encode('utf8')])
                proj_counter += 1

f.close()
g.close()

    # f.write(str(year) + '\n\n')
    # # # print(str(year) + '\n\n')
    # for num in range(len(project_list)):
    #     # print 'Project: ', (project_list[num]).encode("utf8")
    #     # print 'Student: ', student_list[num].encode("utf8")
    #     # print 'Mentor: ', mentor_list[num].encode("utf8")
    #     f.write('Project: ')
    #     f.write((project_list[num]).encode('utf-8'))
    #     f.write('\n')
    #     f.write('Student: ')
    #     f.write((student_list[num]).encode('utf-8'))
    #     f.write('\n')
    #     f.write('Mentor: ')
    #     f.write((mentor_list[num]).encode('utf-8'))
    #     f.write('\n')
    #     # if num > 30:
    #     #     break
    # # print('\n\n')
    # f.write('\n\n')

    # print student_list
    # print "\n\n\nLength: ", len(student_list)

    # g.write(str(year) + '\n\n')
    # for num in range(len(org_ids)):
    #     orgNumWriter.writerow([str(year), org_list[num], str(org_tally[num])])
    #     g.write('Organization: ')
    #     g.write(org_list[num])
    #     g.write('\n')
    #     g.write('Number of Projects: ')
    #     g.write(str(org_tally[num]))
    #     g.write('\n')
    # g.write('\n\n')

# f.close()
# g.close()
