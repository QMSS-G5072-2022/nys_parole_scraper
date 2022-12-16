# nys_parole_scraper

A package for scraping parole information from the NYS DOCCS public site.

Given an input of a csv files with identifying information of individuals (NYSID (New York state ID) or Name and DOB), this package will search for them via the [New York State DOCCS parolee lookup](https://publicapps.doccs.ny.gov/ParoleeLookup/default) and return all parole information, and summary statistics, for the individuals who are found in the system. 

## Use Case
This package was created to aid in the data collection efforts of service providers working with justice-involved populations. Organizations who are in need of parole information of their clients/participants to either further their own program design and evaluation or to successfully report to funders can use this package to do so. 

## Before you start

### Make sure you have Firefox installed as a browser on your computer
This package depends on using a headless Firefox browser. Make sure Firefox is installed on your computer before proceeding. Click [here](https://www.mozilla.org/en-US/firefox/new/?utm_medium=paidsearch&utm_source=google-rsa&utm_campaign=firefox-for-families&utm_content=A144_A203_301421&gclid=Cj0KCQiAqOucBhDrARIsAPCQL1Y1mhZc-bWiI1LXtW6IwfMGvn0WNIB4EV4x_A6z_9Sc8DHNEjDXL3YaAud1EALw_wcB) to download if you don't have it already. 

### Install Geckodriver and add to your Path variables
This package depends on 


## Installation

```bash
$ pip install nys_parole_scraper
```

## Usage

### Input 
This package requires that users provide identifying information that tells the scraper who to search the DOCCS parole database for. 

The input must be a .CSV file, and can live anywhere in you files. The .CSV file should must include the following columns, though they can be in any order:
- Unique ID (optional)
- NYSID (optional if first name, last name, and DOB provided)
- First Name (optional if accurate NYSID is provided)
- Last Name (optional if accurate NYSID is provided)
- DOB (optional if accurate NYSID is provided)

"Unique ID" refers to any unique identification system that your organization may use to identify clients/participants. This is meant to more easily link the returned data to yor own database. It is optional, and if some or all participants do not have a unique ID provided it will not impact the scraping. 

#### See below for sample .CSV setups: 

The scraper would search the DOCCS Parolee Lookup for all of the individuals shown below. Where the NYSID is missing, the first name, last name, and DOB are all provided. Where the DOB is missing, the NYSID is provided. And finally, all NYSIDs have the potential to be accurate, barring any data entry errors (NYSIDs are composed of 8 digits followed by one letter. If NYSIDs provided in the .CSV are not in this format, they will not be searched for as they are not accurate NYSID numbers.) Note that the UNique ID is optional, and the last person listed does not have one - that's okay!

| Unique ID      | NYSID | First Name     | Last Name | DOB |
| ----------- | ----------- |----------- | ----------- | ----------- |
| 19947      | 12345678A       | John     |  Doe        |    |
| 566657   | 12345678B        |  Jane       |    Doe     | 02/04/2008  |
| 928737      |               |   John      |   Smith     | 02/04/2008   |
|          | 12345678C        |   Jane       |   Smith    | 02/04/2008  |


Of the individuals in the sample below, only the last individual, Jane Smith, would be searched for. The first individual has an invalid NYSID composed of only 6 numbers followed by a letter. The second individual listed has a NYSID of "00000009", which is an invalid NYSID sometimes temporarily given to unknown individuals in custody. The third individual listed has no NYSID, but does not have completed first name, last name, and DOB lsited.  

| Unique ID      | NYSID | First Name     | Last Name | DOB |
| ----------- | ----------- |----------- | ----------- | ----------- |
| 19947      | 123456A       | John     |  Doe        |    |
| 566657   | 000000009        |  Jane       |    Doe     | 02/04/2008  |
| 928737      |               |   John      |        | 02/04/2008   |
| 884921   | 12345678C        |   Jane       |   Smith    | 02/04/2008  |


### Using the package

There are two potential ways to use the package. 

If you are only interested in the CSV and Excel output of the scraped parole data and the summary statistics, you can do as follows: 

```
from nys_parole_scraper import parole_scraper

file_path = "C:/Users/parole_scraping/client_info.csv"
dir = "C:/Users/parole_scraping/Output_Folder"
parole_scraper(file_path, dir)
```
This will export a CSV file with all scraped data collected and an Excel file with summary statistics to a new timestamped folder in the designated directory. Output will also be returned in the console. 

If you want to explore, analyze, or modify the data  using python, and would like the output returned as python objects, you can assign the function to two variables, the first being the scraped output and the second being a list that will contain the summary statistic dataframes. For example: 

```
from nys_parole_scraper import parole_scraper

file_path = "C:/Users/parole_scraping/client_info.csv"
dir = "C:/Users/parole_scraping/Output_Folder"
full_output, stats_list = parole_scraper(file_path, dir)
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`nys_parole_scraper` was created by Kellyann Hayes. It is licensed under the terms of the MIT license.

## Credits

`nys_parole_scraper` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
