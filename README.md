# Scraping clinical trial data

**clinicaltrials.gov** is an important resource of clinical trial data. However, downloading the data from the website can be more time consuming than necessary and there is not a way to download the information on enrollment, inclusion and exclusion criteria. The point of this project is to facilitate downloading such information, that may come in handy, examples of that are when doing a feasability study of clinical trials or when studying the impact of words used in patient selection criteria on the enrollment.

[DISCLAIMER: this code isn't actively maintained and may have some bugs] 
# Dependencies

All the dependencies are specified in the (requirements.txt) file.
run :


```
pip install -r requirements.txt 
```


# Usage

[The tutorial](Tutorial.ipynb) shows an example of usage of the scraper. The module scrapeThisData.py contains the Class ScrapeThatData. You just have to import the class and instanciate it with a specified waiting time threshold for loading lazy web pages. Afterwards , you specify the parameters to the __call__ function of the instanciate object:

 * condition : The condition to search in the clinical trials database
 * listed_attributes: The attributes you wish to appear in the search page, these will also appear in the resulting dataset
 * listed_states: the list of states you want to select in the database
 * amount_of_data: number of studies you wish to scrape
 
 
 
 # Notes and acknowledgments
 
 All data downloaded using this program is from www.clinicaltrials.gov and is part a United States Government Database.
 There is no modification of the data.
 
 
 
