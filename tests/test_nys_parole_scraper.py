import sys
sys.path.append("C:/Users/khaye/mds_course/src/mds/Hayes_Kellyann/Final_Project/nys_parole_scraper")

from nys_parole_scraper import scraper_functions
from nys_parole_scraper import nys_parole_scraper
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

# fake data
data = {'Animal':['Cat', 'Dog', 'Cat', 'Dog', 'Bird'],
        'Color':['Grey', 'Brown', 'Black', 'Brown', 'White'],
        'Weight' : [1,2,3.4,4,1]
        }
df = pd.DataFrame(data)

# freq_table test function
def test_freq_table():
    expected = pd.DataFrame({'Animal':['Cat','Dog','Bird'],'Count':[2, 2, 1],'%':['40.0%', '40.0%', '20.0%']}).set_index('Animal')
    expected.index.name = None
    actual = scraper_functions.freq_table(df, 'Animal')
    assert_frame_equal(expected, actual)
    
# test function for ValueError
def test_valerror1():
    with pytest.raises(ValueError):
        nys_parole_scraper.parole_scraper(1, "C:/test_path")
        
# test function for ValueError
def test_valerror2():
    with pytest.raises(ValueError):
        nys_parole_scraper.parole_scraper(1.56, "C:/test_path")
        
# test function for ValueError
def test_valerror3():
    with pytest.raises(ValueError):
        nys_parole_scraper.parole_scraper("C:/test_path", 1)

# test function for ValueError
def test_valerror4():
    with pytest.raises(ValueError):
        nys_parole_scraper.parole_scraper("C:/test_path", 1.56)