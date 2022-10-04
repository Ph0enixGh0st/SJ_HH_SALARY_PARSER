# Programming vacancies compare

The script allows to compare salaries of IT vacancies located in Moscow. 


### How to install

Using GitHub CLI:
```bash
gh repo clone Ph0enixGh0st/SJ_HH_SALARY_PARSER
```

Or download and unpack ZIP file from GIT Hub repository: https://github.com/Ph0enixGh0st/SJ_HH_SALARY_PARSER.git


# Prerequisites

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
In order to run the scripts you will also need SuperJob API Key and SuperJob Client ID.
Both can be obtained here: https://api.superjob.ru/register
API will require to provide a web-site, you can use any web-site address you like.

Next step is to create a ".env" file in the same folder with the scripts.
Please write down the following lines in your .env file and save the file:
```
CLIENT_ID={your SuperJob Client ID here (4 digits)}
API_KEY={your SuperJob API Key here}


# hh_sj_salary_parse.py

The script allows to compare IT vacancies salaries for Moscow downloaded from hh.ru and superjob APIs.


## How to run

```bash
python hh_sj_salary_parse.py
```








### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).


