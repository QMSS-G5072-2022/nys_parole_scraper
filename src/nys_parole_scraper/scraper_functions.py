# -*- coding: utf-8 -*-
"""
@author: khayes
"""
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#=============================================================================
# FUNCTION: SCRAPE TABLE 1
#=============================================================================

def scrape_table1(driver, df):
    #global df
    ##Table 1 - "ParoleeInformation"
    tbl1= driver.find_element(By.XPATH,
                              "//*[@id='MainContent_paroleeInformation']"
                             ).get_attribute('outerHTML')
    df  = pd.read_html(tbl1)
    df = df[0]
    df = df.transpose()
    df.columns = df.iloc[0]
    df = df[1:]
    return df

#=============================================================================
# FUNCTION: SCRAPE TABLE 2
#=============================================================================

def scrape_table2(driver, df):
    ##If Table 2 (supervision info) exists, scrape:
    tbl2= driver.find_element(By.XPATH,
        "//*[@id='MainContent_supervisionInformation']"
        ).get_attribute('outerHTML')
    df2  = pd.read_html(tbl2)
    df2 = df2[0]
    df2 = df2.transpose()

    df2.columns = df2.iloc[0]
    df2 = df2[1:]
    df = pd.merge(df, df2, how="cross")
    return df

#=============================================================================
# FUNCTION: SCRAPE TABLE 3
#=============================================================================

def scrape_table3(driver, df, uid):
    #if offense table exists:
    tbl3= driver.find_element(By.XPATH,
        "//*[@id='MainContent_offenseInformationTable']"
        ).get_attribute('outerHTML')
    df3  = pd.read_html(tbl3)
    df3 = df3[0]
    df3 = df3.transpose()
    df3 = df3.reset_index()
    df3 = df3.drop(columns=['index'])
    
    dic = {0: [], 1: [], 
           2: [], 3: [], 
           4: [], 5: [],
           6: [], 7: [],
           8: [], 9: []}
    
    ################## Row 1 - Charges
    df3_row1 = pd.DataFrame(data = dic)
    
    df3_row1 = df3_row1.append(df3.iloc[[0]])
    
    df3_row1.rename(columns={0: 'Crime of conviction 1', 
                             1: 'Crime of conviction 2',
                             2: 'Crime of conviction 3',
                             3: 'Crime of conviction 4',
                             4: 'Crime of conviction 5',
                             5: 'Crime of conviction 6',
                             6: 'Crime of conviction 7',
                             7: 'Crime of conviction 8',
                             8: 'Crime of conviction 9',
                             9: 'Crime of conviction 10'}, inplace=True)
    
    df = pd.merge(df, df3_row1, how="cross")
    
    #################### Row 2 - Classes
    df3_row2 = pd.DataFrame(data = dic)
    
    df3_row2 = df3_row2.append(df3.iloc[[1]])
    
    df3_row2.rename(columns={0: 'Class 1', 
                             1: 'Class 2',
                             2: 'Class 3',
                             3: 'Class 4',
                             4: 'Class 5',
                             5: 'Class 6',
                             6: 'Class 7',
                             7: 'Class 8',
                             8: 'Class 9',
                             9: 'Class 10'}, inplace=True)
    
    df = pd.merge(df, df3_row2, how="cross")
    
    ######################## Row 3 - Boroughs
    df3_row3 = pd.DataFrame(data = dic)
    
    df3_row3 = df3_row3.append(df3.iloc[[2]])
    
    df3_row3.rename(columns={0: 'County 1', 
                             1: 'County 2',
                             2: 'County 3',
                             3: 'County 4',
                             4: 'County 5',
                             5: 'County 6',
                             6: 'County 7',
                             7: 'County 8',
                             8: 'County 9',
                             9: 'County 10'}, inplace=True)
    
    df = pd.merge(df, df3_row3, how="cross")
    #df["parid"] = uid
    df.insert(loc = 0,
          column = 'ID',
          value = uid)
    return df


#==========================================================
# DEFINE NEW SEARCH
#==========================================================
def new_search(driver, wait):
    wait.until(EC.visibility_of_element_located((
        By.XPATH, "//*[@id='MainContent_NewSearch']"))) 
    driver.find_element(By.XPATH, "//*[@id='MainContent_NewSearch']").click()
    
    
#==========================================================
# DEFINE FREQUENCY TABLE FUNCTION
#==========================================================
def freq_table(df, column, col_name):
    """
    Create a  frequency table.
    
    Parameters
    ----------
    df : pandas DataFrame
        the dataFrame witht he data you would like to create a frequency table of
        
    column : String
        The column in the dataframe you would like to make a frequency table of.
        
    col_name : String
        The name you would like to give to the first column of the returned DataFrame


    Returns
    -------
    To return the following python objects as DataFrames, assign the function to 
    two variables (ex: df1, df2 = parole_scraper(file_path, directory)). To only export 
    the dataframes to the provided directory, you do not need to assign the 
    function to variables (ex: parole_scraper(file_path, directory))
    
    df : console output or pandas DataFrame if assigned to variable
                
    Example
    -------- 
    Returning DataFrames object: 
    >>> from nys_parole_scraper import scraper_functions as sf
    >>> data = {'animal':['Cat', 'Dog', 'Cat', 'Dog', 'Bird'],
            'color':['Grey', 'Brown', 'Black', 'Brown', 'White'],
            'weight' : [1,2,3.4,4,1]
            }
    >>> df = pd.DataFrame(data)
    >>> animal_frequency = sf.freq_table(df, 'animal', 'Animals')
    animal_frequency
    
    Animals | Count  |   %
    ------------------------
    Cat     |   2    | 40.0%
    Dog     |   2    | 40.0%
    Bird    |   1    | 20.0%
    
    
    Returning frequency table only in console output: 
    >>> from nys_parole_scraper import scraper_functions as sf
    >>> data = {'animal':['Cat', 'Dog', 'Cat', 'Dog', 'Bird'],
            'color':['Grey', 'Brown', 'Black', 'Brown', 'White'],
            'weight' : [1,2,3.4,4,1]
            }
    >>> df = pd.DataFrame(data)
    >>> sf.freq_table(df, 'animal', 'Animals')
    
    Animals | Count  |   %
    ------------------------
    Cat     |   2    | 40.0%
    Dog     |   2    | 40.0%
    Bird    |   1    | 20.0%
    
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError('column argument must be a string')
    if not isinstance(column, str):
        raise ValueError('column argument must be a string')
    if not isinstance(col_name, str):
        raise ValueError('col_name argument must be a string')
    c = df[column].value_counts(dropna=False)
    p = df[column].value_counts(dropna=False, normalize=True).mul(100).round(1).astype(str) + '%'
    df_new = pd.concat([c,p], axis=1, keys=['Count', '%'])
    df_new.index.rename(col_name, inplace=True) 
    df_new.reset_index(inplace = True)
    return df_new
