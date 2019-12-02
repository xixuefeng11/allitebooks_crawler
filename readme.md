# Project Description
Crawler using python scrapy to scrape all books from allitebooks.com
* Crawl books and its cover images.
* Each book is in the directory that is named by title.

# Environment
* python 3.6.8+
* python scrapy

# Running
## Install python packages
``` Command Prompt
pip install -r requirements.txt
```
## Run the spider
``` Command Prompt
scrapy crawl allitebooksspider -o books.json
```
