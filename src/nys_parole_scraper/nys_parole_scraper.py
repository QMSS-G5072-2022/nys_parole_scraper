# -*- coding: utf-8 -*-
"""
@author: khayes
"""

# import libraries
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.by import By
import numpy as np
import os
from datetime import date
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nys_parole_scraper import scraper_functions as sf
# changed from just " import scraper_functions as sf "
### making this change, and moving all files from src>nys_parole_scraper to just src, and then importing scraper as "from  nys_parole_scraper.nys_parole_scraper import parole_scraper" (alternatively could do "from nys_scraper import nys_scraper" and then use nys_scraper.parole_scraper as function call). This change allows both this to work as well as pytest
from selenium.webdriver.firefox.options import Options

def parole_scraper(file_path, directory): 
    """
    Scrapes NYS parole information from the NYS DOCCS parolee lookup website 
    based on user inputs and returns a clean dataset and summary statistics.
    
    Parameters
    ----------
    file_path : String
        A string representing the path of the CSV file that includes the identifying 
        information of the individuals to be searched for with the scraper. See 
        Readme for more information of the input csv file construction.
    directory : String
        A string representing the folder path where the user would like an output 
        folder created, in which the final dataset and summary statistics will 
        be exported.

    Returns
    -------
    To return the following python objects as DataFrames, assign the function to 
    two variables (ex: df1, df2 = parole_scraper(file_path, directory)). To only export 
    the dataframes to the provided directory, you do not need to assign the 
    function to variables (ex: parole_scraper(file_path, directory))
    
    full_output : pandas DataFrame, CSV
        The concatenated parole information of all provided individuals found
        in the DOCCS parole database. The returned dataframe will take on 
        whatever name you assign first to the the function. 
        Example: df1, df2 = parole_scraper(file_path, directory)
            full_output will be returned as df1
            
        full_putput will also be exported as a csv to an output folder in the 
        directory provided by the directory parameter.
    
    stats_list: List, Excel
        A list of the Following DataFrames, returned as the second varible assigned 
        to the function call. All summary statistics and frequency table objects 
        will be exported in separate sheets of an Excel file in the same output
        folder.
            
            stats_numeric : pandas DataFrame
                Summary statistics on age; length of time between release to 
                parole and current date in months; and number of convictions
            
            race_freq : pandas DataFrame
                Frequency table of race/ethncity
            
            age_freq : pandas DataFrame
                Frequency table of age groups
            
            pstatus_freq : pandas DataFrame
                Frequency table of current parole status
                
            county_unique_freq : pandas DataFrame
                Frequency table of unique individuals with convictions in each county
                
            top_charge_freq : pandas DataFrame
                Frequency table of top charges
                
            convictions_freq : pandas DataFrame
                Frequency table of unique individuals per charge type (every
                conviction, not only top charge)
                        
    Example
    -------- 
    Returning DataFrames as objects: 
    >>> from parole_scrpaer_MDS import parole_scraper
    >>> file_path = "C:/Users/parole_scraping.csv"
    >>> directory = "C:/Users/Output_Folder"
    >>> df1, df_list = parole_scraper(file_path, directory)
    df1 = full_output
    df_list = stats_list
    full_output exported as CSV
    stats_list exported as Excel
    
    Without returning DataFrames as objects: 
    >>> from parole_scrpaer_MDS import parole_scraper
    >>> file_path = "C:/Users/parole_scraping.csv"
    >>> directory = "C:/Users/Output_Folder"
    >>> parole_scraper(file_path, directory)
    full_output exported as CSV
    stats_list exported as Excel
    
    """
    if isinstance(file_path, int):
        raise ValueError('File_path argument must be a string')
    if isinstance(file_path, float):
        raise ValueError('File_path argument must be a string')
    if isinstance(directory, int):
        raise ValueError('directory argument must be a string')
    if isinstance(directory, float):
        raise ValueError('directory argument must be a string')
    
    
    assert os.path.isfile(file_path) != False, "file_path argument must be a path to an existing file. Please check your input."
    assert os.path.isdir(directory) != False, "directory argument must be the path to an existing directory. Please check your input."
            
    #create date and time variable and make directory name
    now = datetime.now()
    dyn_dir_name = now.strftime("%Y%m%d_%H.%M.%S")
    
    # create today variables for adding to dataset and computing date differences
    now_today = date.today()
    today_str = now_today.strftime("%m/%d/%Y")
    today = datetime.strptime(today_str, "%m/%d/%Y")    
    
    #create directory
    global output_dir
    output_dir = directory+"/Output_"+dyn_dir_name
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    #Import file with scraping info as csv
    data_csv = pd.read_csv(file_path, delimiter=',', dtype='str')
        
    #strip white spaces
    for col in ('NYSID', 
                'First Name',
                'Last Name', 
                'DOB', 
                'Unique ID'):
        data_csv[col] = data_csv[col].astype(str).str.strip()

    #rename columns
    data_csv = data_csv.rename(columns={'First Name': 'first', 'Last Name': 'last', 'DOB': 'dob', 'Unique ID': 'id'})
    
    # create year column
    data_csv['year'] = data_csv['dob'].str.extract(r'(\d\d\d\d)$')
    
    # create df of nysids and id only
    nysids_start = data_csv.drop(columns=['first', 'last', 'dob'])
    
    # keep only NYSIDS with 9 didgits followed by letter
    nysids = nysids_start[nysids_start['NYSID'].str.contains(r'^\d\d\d\d\d\d\d\d[A-Za-z]$')]
    # keep only NYSIDS that do not have "00000" - these are fake nysids given by state when NYSID is unknown
    nysids = nysids[nysids['NYSID'].str.contains(r'^(?!00000)')]
    
    # outer merge with data_csv
    outer_join = data_csv.merge(nysids, how = 'outer', indicator = True)
    
    # anti-join to get names that need to be scraped
    names = outer_join[~(outer_join._merge == 'both')].drop('_merge', axis = 1)
    
    # specify the url (DOCCS)
    urlpage = 'https://publicapps.doccs.ny.gov/ParoleeLookup/default' 
    
    # run firefox webdriver from executable path
    global driver
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    
    # get web page
    driver.get(urlpage)
    # sleep for 5s to allow page to fully load
    time.sleep(5)
    
    # create emtpy df and list to append individuals' scraped data to as dataframes
    global dataframe
    dataframe = pd.DataFrame()
    global df_list 
    df_list = []
    
    # global wait
    global wait
    wait = WebDriverWait(driver, 30)
    
    #=========================================================================
    #LOOP BEGINS HERE
    #=========================================================================
    
    #Wait until page is fully loaded and nysid field is available
    for x,e in zip(nysids['NYSID'], nysids['id']): 
        
        wait.until(EC.visibility_of_element_located((
            By.XPATH, "//*[@id='MainContent_txtNysid']")))
       
        #find nysid entry by xpath
        nysid_search = driver.find_element(
            By.XPATH, "//*[@id='MainContent_txtNysid']")
        
        # find submit button by xpath_homepage
        submit = driver.find_element(By.XPATH,
                                     "//*[@id='MainContent_BtnSubmit']")
     
        # Enter nysid in first searchbar
        nysid_search.send_keys(x)
        
        # Click Submit
        submit.click()
        
        #Check if nysid was not found
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_paroleeInformation']")
        except NoSuchElementException:
            wait.until(EC.visibility_of_element_located((
                By.XPATH, "//*[@id='MainContent_NewSearch']"))) 
            newsearch = driver.find_element(By.XPATH, "//*[@id='MainContent_NewSearch']")
            newsearch.click()
            
            continue
    
    #==========================================================================
    ## SCRAPE DATA:
    #==========================================================================
    
        ##Table 1 - "ParoleeInformation"
        dataframe = sf.scrape_table1(driver, dataframe) 
        
        ##Table 2 - "SupervisionInformation"
        #######Check that Table 2 exists
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_supervisionInformation']/tbody/tr[1]/td[1]")
        except NoSuchElementException:
            try: 
                check = driver.find_element(By.XPATH,
                    "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
            except NoSuchElementException: # if neither supervision nor offense tables exist
                #export_nysid_df(dataframe)
                df_list.append(dataframe)
               
                #Go back to home page
                sf.new_search(driver, wait)
                continue 
            
            #if offense table exists:
            dataframe = sf.scrape_table3(driver, dataframe, e)
            
            #export to csv:
            df_list.append(dataframe)
                       
            #Go back to home page
            sf.new_search(driver, wait)
        
            continue
        
        ##If Table 2 (supervision info) exists, scrape:
        dataframe = sf.scrape_table2(driver, dataframe)
        
        ##Table 3 - "OffenseInformation"
        #######Check that Table 3 exists
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
        except NoSuchElementException:
            #export
            df_list.append(dataframe) 
            
            #Go back to home page
            sf.new_search(driver, wait)

            continue
    
        #If Table 3 exists, scrape:
        dataframe = sf.scrape_table3(driver, dataframe, e)
        
        #####Done Scraping
        
        df_list.append(dataframe)
        
        sf.new_search(driver, wait)
        
    #==============================================================================
    # LOOP THROUGH NAMES
    #==============================================================================
    
    for a,b,c,d,e in zip(names['first'], names['last'], names['dob'], names['year'], names['id']):
        wait.until(EC.visibility_of_element_located((
            By.XPATH, "//*[@id='MainContent_txtFName']"))) 
       
        #find first name entry by xpath
        first_search = driver.find_element(
            By.XPATH, "//*[@id='MainContent_txtFName']")
        
        #find last name entry by xpath
        last_search = driver.find_element(
            By.XPATH, "//*[@id='MainContent_txtLName']")
        
        #find last name entry by xpath
        year_search = driver.find_element(By.XPATH, "//*[@id='MainContent_txtYob']")
        
        # find submit button by xpath_homepage
        submit = driver.find_element(By.XPATH,
                                     "//*[@id='MainContent_BtnSubmit']")
     
        
        # Enter first name in first searchbar
        first_search.send_keys(a)
        
        # Enter last name in first searchbar
        last_search.send_keys(b)    
        
        # Enter year in year searchbar
        year_search.send_keys(d) 
        
        # Click Submit
        submit.click()
        
        #Check if name was not found
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_manyResultsDiv']")
        except NoSuchElementException:
            sf.new_search(driver, wait)
            continue
        
        try: # check if there is a DOB match on page 1 of results
            check = driver.find_element(By.XPATH, "//tr[td='" + c + "']")
        except NoSuchElementException: 
            try: # if no DOB match, check if page 2 exists
                wait.until(EC.visibility_of_element_located((
                    By.XPATH, "//*[@id='MainContent_navRowTable']")))
                check = driver.find_element(By.LINK_TEXT, '2')
            except NoSuchElementException: # if page 2 does not exist, restart loop
                sf.new_search(driver, wait)
                continue
            
            # if page 2 exists, go to page 2
            page = driver.find_element(By.LINK_TEXT, '2').click() 
            
            # check if there are DOB matches on page two
            try: 
                check = driver.find_element(By.XPATH, "//tr[td='" + c + "']")
            except NoSuchElementException:
                try:  # if no DOB match, check if page 3 exists
                    wait.until(EC.visibility_of_element_located((
                        By.XPATH, "//*[@id='MainContent_navRowTable']")))
                    check = driver.find_element(By.LINK_TEXT, '3')
                except NoSuchElementException: # if page 3 does not exist, restart loop
                    sf.new_search(driver, wait)
                    continue
                
                # if page 3 exists, go to page 3
                page = driver.find_element(By.LINK_TEXT, '3').click() 
                
                # check if there are DOB matches on page 3
                try: 
                    check = driver.find_element(By.XPATH, "//tr[td='" + c + "']")
                except NoSuchElementException:
                    try:  # if no DOB match, check if page 4 exists
                        wait.until(EC.visibility_of_element_located((
                            By.XPATH, "//*[@id='MainContent_navRowTable']")))
                        check = driver.find_element(By.LINK_TEXT, '4')
                    except NoSuchElementException: # if page 4 does not exist, restart loop
                        sf.new_search(driver, wait)
                        continue
                   
                    # if page 4 exists, go to page 4
                    page = driver.find_element(By.LINK_TEXT, '4').click()
                    
                    try: 
                        check = driver.find_element(By.XPATH, "//tr[td='" + c + "']")
                    except NoSuchElementException: # if DOB match not found continue
                        sf.new_search(driver, wait)
                        continue
                    
                    #=============================================================
                    #SCRAPE RESULT FROM PAGE 4
                    #=============================================================
                    
                    #click on name
                    link =  driver.find_element(By.XPATH, "//tr[td='" + c + "']/td/preceding-sibling::td[3]")
                    link.click()
    
                    ##Table 1 - "ParoleeInformation"
                    dataframe = sf.scrape_table1(driver, dataframe) 
                    
                    ##Table 2 - "SupervisionInformation"
                    #######Check that Table 2 exists
                    try: 
                        check = driver.find_element(By.XPATH,
                            "//*[@id='MainContent_supervisionInformation']/tbody/tr[1]/td[1]")
                    except NoSuchElementException:
                        try: 
                            check = driver.find_element(By.XPATH,
                                "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
                        except NoSuchElementException: # if neither supervision nor offense tables exist
                            
                            df_list.append(dataframe)

                            #Go back to home page
                            sf.new_search(driver, wait)
                            
                            continue 
                        
                        #if offense table exists:
                        dataframe = sf.scrape_table3(driver, dataframe, e)
                        
                        #export to csv:
                        df_list.append(dataframe)
                        
                        #Go back to home page
                        sf.new_search(driver, wait)                    
                        continue
                    
                    ##If Table 2 (supervision info) exists, scrape:
                    dataframe = sf.scrape_table2(driver, dataframe)
                    
                    ##Table 3 - "OffenseInformation"
                    #######Check that Table 3 exists
                    try: 
                        check = driver.find_element(By.XPATH,
                            "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
                    except NoSuchElementException:
                        #export
                        df_list.append(dataframe)
                       
                        #Go back to home page
                        sf.new_search(driver, wait)                        

                        continue
    
                    #If Table 3 exists, scrape:
                    dataframe = sf.scrape_table3(driver, dataframe, e)
                    
                    #####Done Scraping
                    
                    #export
                    df_list.append(dataframe)
                                       
                    #Go back to home page
                    sf.new_search(driver, wait)
                    
                    continue
                #=============================================================
                #SCRAPE RESULT FROM PAGE 3
                #=============================================================
                
                #click on name
                link =  driver.find_element(By.XPATH, "//tr[td='" + c + "']/td/preceding-sibling::td[3]")
                link.click()
                ##Table 1 - "ParoleeInformation"
                dataframe = sf.scrape_table1(driver, dataframe) 
                
                ##Table 2 - "SupervisionInformation"
                #######Check that Table 2 exists
                try: 
                    check = driver.find_element(By.XPATH,
                        "//*[@id='MainContent_supervisionInformation']/tbody/tr[1]/td[1]")
                except NoSuchElementException:
                    try: 
                        check = driver.find_element(By.XPATH,
                            "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
                    except NoSuchElementException: # if neither supervision nor offense tables exist

                        df_list.append(dataframe)
                       
                        #Go back to home page
                        sf.new_search(driver, wait)
                        continue 
                    
                    #if offense table exists:
                    dataframe = sf.scrape_table3(driver, dataframe, e)
                    
                    #export to csv:
                    df_list.append(dataframe)
                   
                    #Go back to home page
                    sf.new_search(driver, wait)
                
                    continue
                
                ##If Table 2 (supervision info) exists, scrape:
                dataframe = sf.scrape_table2(driver, dataframe)
                
                ##Table 3 - "OffenseInformation"
                #######Check that Table 3 exists
                try: 
                    check = driver.find_element(By.XPATH,
                        "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
                except NoSuchElementException:
                    #export
                    df_list.append(dataframe)
                    
                    #Go back to home page
                    sf.new_search(driver, wait)

                    continue
    
                #If Table 3 exists, scrape:
                dataframe = sf.scrape_table3(driver, dataframe, e)
                
                #####Done Scraping
                
                #export
                #export_name_df()
                df_list.append(dataframe)
                               
                #Go back to home page
                sf.new_search(driver, wait)
                continue
                
            #=============================================================
            #SCRAPE RESULT FROM PAGE 2
            #=============================================================
            
            #click on name
            link =  driver.find_element(By.XPATH, "//tr[td='" + c + "']/td/preceding-sibling::td[3]")
            link.click()
            ##Table 1 - "ParoleeInformation"
            dataframe = sf.scrape_table1(driver, dataframe) 
            
            ##Table 2 - "SupervisionInformation"
            #######Check that Table 2 exists
            try: 
                check = driver.find_element(By.XPATH,
                    "//*[@id='MainContent_supervisionInformation']/tbody/tr[1]/td[1]")
            except NoSuchElementException:
                try: 
                    check = driver.find_element(By.XPATH,
                        "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
                except NoSuchElementException: # if neither supervision nor offense tables exist
                    #export_name_df()
                    df_list.append(dataframe)
                                       
                    # #Go back to home page

                    sf.new_search(driver, wait)
                    continue 
                
                #if offense table exists:
                dataframe = sf.scrape_table3(driver, dataframe, e)
                
                #export to csv:
                df_list.append(dataframe)
               
                #Go back to home page
                sf.new_search(driver, wait)
            
                continue
            
            ##If Table 2 (supervision info) exists, scrape:
            dataframe = sf.scrape_table2(driver, dataframe)
            
            ##Table 3 - "OffenseInformation"
            #######Check that Table 3 exists
            try: 
                check = driver.find_element(By.XPATH,
                    "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
            except NoSuchElementException:
                #export
                df_list.append(dataframe)
                               
                #Go back to home page
                sf.new_search(driver, wait)

                continue
    
            #If Table 3 exists, scrape:
            dataframe = sf.scrape_table3(driver, dataframe, e)
            
            #####Done Scraping
            
            #export
            df_list.append(dataframe)
            
            #Go back to home page
            sf.new_search(driver, wait)
            
            continue
        #=============================================================
        #SCRAPE RESULT FROM PAGE 1
        #=============================================================
        
        #click on name
        link =  driver.find_element(By.XPATH, "//tr[td='" + c + "']/td/preceding-sibling::td[3]")
        link.click()
        
        ##Table 1 - "ParoleeInformation"
        dataframe = sf.scrape_table1(driver, dataframe) 
        
        ##Table 2 - "SupervisionInformation"
        #######Check that Table 2 exists
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_supervisionInformation']/tbody/tr[1]/td[1]")
        except NoSuchElementException:
            try: 
                check = driver.find_element(By.XPATH,
                    "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
            except NoSuchElementException: # if neither supervision nor offense tables exist
                #export_name_df()
                df_list.append(dataframe)
                               
                #Go back to home page
                sf.new_search(driver, wait)
                
                continue 
            
            #if offense table exists:
            dataframe = sf.scrape_table3(driver, dataframe, e)
            
            #export to csv:
            df_list.append(dataframe)
                       
            #Go back to home page
            sf.new_search(driver, wait)
        
            continue
        
        ##If Table 2 (supervision info) exists, scrape:
        dataframe = sf.scrape_table2(driver, dataframe)
        
        ##Table 3 - "OffenseInformation"
        #######Check that Table 3 exists
        try: 
            check = driver.find_element(By.XPATH,
                "//*[@id='MainContent_offenseInformationTable']/tbody/tr[2]/td[1]")
        except NoSuchElementException:
            #export
            df_list.append(dataframe)
            
            # find new search button by xpath
            sf.new_search(driver, wait)

            continue
    
        #If Table 3 exists, scrape:
        dataframe = sf.scrape_table3(driver, dataframe, e)
        
        #####Done Scraping
        
        #export
        df_list.append(dataframe) 
        
        # find new search button by xpath
        sf.new_search(driver, wait)
        
        
    #=============================================================================
    # END OF LOOPS - CONCAT AND EXPORT AS CSV
    #=============================================================================

    #end loop; close driver
    driver.close()
    driver.quit()
       
    # concatenate all nysid dfs
    global full_output
    full_output = pd.concat(df_list)
    
    #Capitalize certain columns
    for col in ('Name:', 
                'Parole status:',
                'Class 1', 
                'Class 2', 
                'Class 3', 
                'Class 4', 
                'Class 5',
                'Class 6', 
                'Class 7', 
                'Class 8', 
                'Class 9', 
                'Class 10',
                'County 1', 
                'County 2', 
                'County 3', 
                'County 4', 
                'County 5',
                'County 6', 
                'County 7', 
                'County 8', 
                'County 9', 
                'County 10'):
        full_output[col] = full_output[col].fillna("")
        full_output[col] = full_output[col].astype(str).str.title()
    
    # Add column indicating day data was scraped
    full_output["Date Info Scraped:"] = today #today_str !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
    # #Turn dates into datetime objects 
    # full_output[["Date of birth:", "Release to parole supervision:"]]= full_output[["Date of birth:", "Release to parole supervision:"]].astype('datetime64[ns]')
    full_output[["Date of birth:", "Release to parole supervision:", "Effective date:"]]= full_output[["Date of birth:", "Release to parole supervision:","Effective date:"]].astype('datetime64[ns]')
    
    # Add age column
    idob = full_output.columns.get_loc("Date of birth:") # get index location of DOB
    age = (today - full_output["Date of birth:"]) / np.timedelta64(1, 'Y') # get series of ages
    age = np.floor(age) # get actual age, no decimals

    full_output.insert(loc = idob +1,
              column = 'Age:',
              value = age) #insert new age column directly after DOB column
    
    # Add months since release column
    irel = full_output.columns.get_loc("Release to parole supervision:") # get index location of release date
    mrelease = (today - full_output["Release to parole supervision:"]) / np.timedelta64(1, 'M') # get series
    mrelease = np.around(mrelease, decimals=1, out=None) # round to 1 decimal

    full_output.insert(loc = irel +1,
              column = "Months Since Release:",
              value = mrelease) #insert new column directly after release date

    iconv = full_output.columns.get_loc("Crime of conviction 10") 
    count_conv = full_output[['Crime of conviction 1',
           'Crime of conviction 2', 
           'Crime of conviction 3', 
           'Crime of conviction 4', 
           'Crime of conviction 5',
           'Crime of conviction 6', 
           'Crime of conviction 7', 
           'Crime of conviction 8', 
           'Crime of conviction 9', 
           'Crime of conviction 10']].apply(lambda x: x.notnull().sum(), axis='columns')
    
    full_output.insert(loc = iconv +1,
              column = "Total Convictions",
              value = count_conv) # insert total after last conviction column
    
    # make null IDs empty cells
    full_output['ID'] = np.where(
        full_output['ID'] == "nan", '', full_output['ID'])
    
    # make new dataframe for summary stats
    output_stats = full_output.copy()
    
    # change empoty spaces back to nans
    full_output = full_output.replace(r'^\s*$', np.nan, regex=True)
    
    #export to csv
    full_output.to_csv(output_dir + '/parole_full_output_'+ dyn_dir_name +'.csv', index=False, encoding="utf-8")
        
    
    #=============================================================================
    # SUMMARY STATISTICS
    #=============================================================================
    

    # summary stats on continuous variables
    global stats_numeric
    stats_numeric = full_output[["Age:", "Months Since Release:","Total Convictions"]].describe().loc[['count','min','mean','max']]
    
    # create age bins
    bins = [0,20,30,40,50,60,150]
    group_names=['0 - 20','21-30','31-40','41-50','51-60','60 +']
    output_stats['age_bin']=pd.cut(output_stats['Age:'],bins,labels=group_names).astype(object)
    
    global age_freq
    age_freq = sf.freq_table(output_stats, "age_bin", "Age")
    
    # get frequency of unique individuals with cases in different counties
    county_list = ['County 1',
               'County 2', 
               'County 3', 
               'County 4', 
               'County 5',
               'County 6', 
               'County 7', 
               'County 8', 
               'County 9', 
               'County 10']

    output_stats[county_list] = output_stats[county_list].fillna("")

    counties = np.unique(output_stats[county_list].values)
    counties = [item for item in counties if item != ""]
    
    global county_unique_freq
    county_unique_freq = pd.DataFrame(columns=['Count', '%'], index = counties)
    county_unique_freq.index.rename("Counties All Convictions", inplace = True)
    
    for county in counties:
        output_stats[county+'_unique'] = output_stats[['County 1',
                'County 2', 
                'County 3', 
                'County 4', 
                'County 5',
                'County 6', 
                'County 7', 
                'County 8', 
                'County 9', 
                'County 10']].apply(
                    lambda x: x.str.contains(county ,case=False)).any(axis=1).astype(int)
        c = output_stats[county+'_unique'].sum()
        p = str(round((c/len(output_stats.index))*100, 1))+ '%'
        county_unique_freq.loc[county].Count = c
        county_unique_freq.loc[county]['%'] = p
    county_unique_freq.reset_index(inplace = True)

    # frequency tables for race/ethnicity
    global race_freq
    race_freq = sf.freq_table(output_stats, "Race / ethnicity:", "Race/Ethnicity")
    
    # frequency tables for parole status
    global pstatus_freq
    pstatus_freq = sf.freq_table(output_stats, "Parole status:", "Parole Status")
    
    
    # get counts of charges
    conv_list = ['Crime of conviction 1',
               'Crime of conviction 2', 
               'Crime of conviction 3', 
               'Crime of conviction 4', 
               'Crime of conviction 5',
               'Crime of conviction 6', 
               'Crime of conviction 7', 
               'Crime of conviction 8', 
               'Crime of conviction 9', 
               'Crime of conviction 10']

    output_stats[conv_list] = output_stats[conv_list].fillna("")

    convictions = np.unique(output_stats[conv_list].values)
    convictions = [item for item in convictions if item != ""]

    global convictions_freq
    convictions_freq = pd.DataFrame(columns=['Count', '%'], index = convictions)
    convictions_freq.index.rename("Charges All Convictions", inplace = True)
    
    for conv in convictions:
        output_stats[conv+'_unique'] = output_stats[['Crime of conviction 1',
                'Crime of conviction 2', 
                'Crime of conviction 3', 
                'Crime of conviction 4', 
                'Crime of conviction 5',
                'Crime of conviction 6', 
                'Crime of conviction 7', 
                'Crime of conviction 8', 
                'Crime of conviction 9', 
                'Crime of conviction 10']].apply(
                    lambda x: x.str.contains(conv ,case=False)).any(axis=1).astype(int)
        c = output_stats[conv+'_unique'].sum()
        p = str(round((c/len(output_stats.index))*100, 1))+ '%'
        convictions_freq.loc[conv].Count = c
        convictions_freq.loc[conv]['%'] = p
    convictions_freq.reset_index(inplace = True)
    
    #get top charge (crime of conviction #1) fequency table
    global top_charge_freq
    top_charge_freq = sf.freq_table(output_stats, 'Crime of conviction 1', "Top Charge")

    
    ##### Export --------------------------------------------------------------
    
    # Create a Pandas Excel writer
    writer = pd.ExcelWriter(output_dir + '/summary_statistics_'+ dyn_dir_name + '.xlsx', engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    stats_numeric.to_excel(writer, sheet_name='Summary Statistics', index = False)
    age_freq.to_excel(writer, sheet_name='Age', index = False)
    race_freq.to_excel(writer, sheet_name='Race.Ethnicity', index = False)
    pstatus_freq.to_excel(writer, sheet_name='Parole Status', index = False)
    county_unique_freq.to_excel(writer, sheet_name='Unique People per County', 
                                index = False)
    top_charge_freq.to_excel(writer, sheet_name='Top Charge', index = False)
    convictions_freq.to_excel(writer, sheet_name='Unique People per Charge Type',
                              index = False)
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    #create list with stats dataframes
    stats_list = [stats_numeric, 
                  race_freq, 
                  age_freq, 
                  pstatus_freq, 
                  county_unique_freq,
                  top_charge_freq,
                  convictions_freq]
    
    return full_output, stats_list
    

    
   
