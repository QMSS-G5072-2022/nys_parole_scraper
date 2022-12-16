# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 20:27:32 2022

@author: khaye
"""

from parole_scraper_MDS_4 import parole_scraper
from datetime import datetime
from datetime import date
import numpy as np 
import pandas as pd
from test_freq import freq_table
import os, sys
now = date.today()
today_str = now.strftime("%m/%d/%Y")
today = datetime.strptime(today_str, "%m/%d/%Y")


path="C:/Users/khaye/OneDrive/Documents/Parole_Scraping/DATA_FILES/test_data.csv"
dire = "C:/Users/khaye/OneDrive/Documents/Parole_Scraping"
path="test"
dire = "blah blah"
os.path.isfile(path)

output, stats = parole_scraper(path, dire)

if os.path.isfile(path) == False:
    raise ValueError('file_path argument must be a path to an existing file. Please check your input.')
    
os.path.isdir(dire)

os.chir
    
except False: 
    raise ValueError('file_path argument must be a path to an existing file. Please check your input.')


nysids_csv.style.set_caption("NYSIDS DF")
nysids_csv

full_output[["Date of birth:", "Release to parole supervision:"]]= full_output[["Date of birth:", "Release to parole supervision:"]].astype('datetime64[ns]')

#full_output["Age"] = (today - full_output["Date of birth:"]) / np.timedelta64(1, 'Y')
#full_output["Age2"] = np.floor(full_output["Age"])

full_output["Months Since Release to Parole"] = (today - full_output["Release to parole supervision:"]) / np.timedelta64(1, 'M')

full_output["Months Since Release to Parole"] = np.around(full_output["Months Since Release to Parole"], decimals=1, out=None)

full_output["Date Info Scraped:"] = today_str


idob = full_output.columns.get_loc("Date of birth:")
age = (today - full_output["Date of birth:"]) / np.timedelta64(1, 'Y')
age = np.floor(age)

full_output.insert(loc = idob +1,
          column = 'Age:',
          value = age)

irel = full_output.columns.get_loc("Release to parole supervision:")
mrelease = (today - full_output["Release to parole supervision:"]) / np.timedelta64(1, 'M')
mrelease = np.around(mrelease, decimals=1, out=None)

full_output.insert(loc = irel +1,
          column = "Months Since Release:",
          value = mrelease)

convictions_list = ['Crime of conviction 1',
           'Crime of conviction 2', 
           'Crime of conviction 3', 
           'Crime of conviction 4', 
           'Crime of conviction 5',
           'Crime of conviction 6', 
           'Crime of conviction 7', 
           'Crime of conviction 8', 
           'Crime of conviction 9', 
           'Crime of conviction 10']

iconv = full_output.columns.get_loc("Crime of conviction 10") 
count_conv = full_output[[convictions_list]].apply(lambda x: x.notnull().sum(), axis='columns')
full_output.insert(loc = iconv +1,
          column = "Total Convictions",
          value = count_conv)

describe = full_output.describe()

from pandas_profiling import ProfileReport
profile = ProfileReport(full_output, title='Profiling Report', explorative=False)

stats_numeric = full_output[["Age:", "Months Since Release:","Total Convictions"]].describe().loc[['count','min','mean','max']]


# Frequency tables for each categorical feature
crosstab = pd.DataFrame()
for column in full_output[["Race / ethnicity:", "Parole status:", "Senior Parole Officer:"]].select_dtypes(include=['object']).columns:
    table = pd.crosstab(index=full_output[column], columns='% observations', normalize='columns')*100
    crosstab.append(table)

c = full_output["Race / ethnicity:"].value_counts(dropna=False)
p = full_output["Race / ethnicity:"].value_counts(dropna=False, normalize=True).mul(100).round(1).astype(str) + '%'
race = pd.concat([c,p], axis=1, keys=['Count', '%'])

# def freq_table(df, column):    
#     c = df[column].value_counts(dropna=False)
#     p = df[column].value_counts(dropna=False, normalize=True).mul(100).round(1).astype(str) + '%'
#     pd.concat([c,p], axis=1, keys=['Count', '%'])







output_stats = full_output.copy()



# create age bins
bins = [0,20,30,40,50,60,150]
group_names=['0 - 20','21-30','31-40','41-50','51-60','60 +']
output_stats['age_bin']=pd.cut(output_stats['Age:'],bins,labels=group_names).astype(object)

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

county_unique_freq = pd.DataFrame(columns=['Count', '%'], index = counties)
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



# Yes/No for parole officer info
output_stats['Officer Info Provided'] = np.where(output_stats['Senior Parole Officer:'].notnull, 'Yes', 'No')


# create a list of the values we want to assign for each condition
values = ['tier_4', 'tier_3', 'tier_2', 'tier_1']

# create a new column and use np.select to assign values to it using our lists as arguments
#df['tier'] = np.select(conditions, values)


    # new = pd.concat([c,p], axis=1, keys=['Count', '%'])
    # full_output = pd.concat(county_unique_freq, new)

# for col in output_stats[["Race / ethnicity:", "Parole status:", "Senior Parole Officer:"]]
# c = df[column].value_counts(dropna=False)
# p = df[column].value_counts(dropna=False, normalize=True).mul(100).round(1).astype(str) + '%'
# df_new = pd.concat([c,p], axis=1, keys=['Count', '%'])            


race_freq = freq_table(output_stats, "Race / ethnicity:")
pstatus_freq = freq_table(output_stats, "Parole status:")
age_freq = freq_table(output_stats, "age_bin")
officer_freq = freq_table(output_stats, 'Officer Info Provided')
top_charge_freq = freq_table(output_stats, 'Crime of conviction 1')


full_output = pd.read_csv("C:/Users/khaye/OneDrive/Documents/Parole_Scraping/Output_20221215_18.48.32/parole_full_output_20221215_18.48.32.csv", delimiter=',', dtype='str')
top_charge_freq = freq_table(full_output, 'Crime of conviction 1')
# Create a Pandas Excel writer
writer = pd.ExcelWriter(dire + '/summary_statistics.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
stats_numeric.to_excel(writer, sheet_name='Summary Statistics')
age_freq.to_excel(writer, sheet_name='Age')
race_freq.to_excel(writer, sheet_name='Race.Ethnicity')
pstatus_freq.to_excel(writer, sheet_name='Parole Status')
officer_freq.to_excel(writer, sheet_name='P.O. Info Provided')
top_charge_freq
# Close the Pandas Excel writer and output the Excel file.
writer.save()




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
    #p = str(round((c/len(output_stats.index))*100, 1))+ '%'
    convictions_freq.loc[conv].Count = c
    #convictions_freq.loc[conv]['%'] = p



c = output["Crime of conviction 1"].value_counts(dropna=False)
p = output["Crime of conviction 1"].value_counts(dropna=False, normalize=True).mul(100).round(1).astype(str) + '%'
df_new = pd.concat([c,p], axis=1, keys=['Count', '%'])
df_new.index.rename('Top Charge', inplace=True) 