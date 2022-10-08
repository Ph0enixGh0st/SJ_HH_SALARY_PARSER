import datetime
import json
import os
import requests

from datetime import timedelta as tdelta
from dotenv import load_dotenv
from terminaltables import AsciiTable


def fetch_all_vacancies_hh():

    city_id = '1'
    specialization = '1'
    publish_date_from = datetime.datetime.now() - datetime.timedelta(90)
    params = {
        'area': city_id,
        'page': 0,
        'per_page': 100,
        'only_with_salary': 'true',
        'specialization': specialization,
        'date_from': publish_date_from.strftime('%Y-%m-%d')
    }
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=params)
    vacancies = response.json()
    pages_qty = int(vacancies.get('pages'))
    hh_all_vacancies = {}

    count = 0
    count_processed = 0
    salary_pool = 0

    salary_breakdown = {
        'Python': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        },
        'Java': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        },
        'JavaScript': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        }
    }

    language_pool = ['Python', 'Java', 'JavaScript']
    avg_salary_python = 0
    avg_salary_java = 0
    avg_salary_js = 0

    for language in language_pool:

        for page in range(0, pages_qty):

            params['page'] = page
            one_page_vacancies = requests.get(url, params=params)
            hh_all_vacancies.update(one_page_vacancies.json())

            for item in range(0, hh_all_vacancies['per_page']):

                if str(language) in hh_all_vacancies['items'][item]["name"]:

                    salary_breakdown[language]['count'] += 1

                    if hh_all_vacancies['items'][item]['salary'] is not None and hh_all_vacancies['items'][item]['salary']['currency'] == 'RUR':
                        currency = hh_all_vacancies['items'][item]['salary']['currency']
                        salary_from = hh_all_vacancies['items'][item]['salary']['from']
                        salary_to = hh_all_vacancies['items'][item]['salary']['to']
                        salary_breakdown[language]['count_processed'] += 1
                        salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))

        if salary_breakdown['Python']['count_processed'] != 0:
            avg_salary_python = int((salary_breakdown['Python']['salary_pool'])/(salary_breakdown['Python']['count_processed']))
        if salary_breakdown['Java']['count_processed'] != 0:
            avg_salary_java = int((salary_breakdown['Java']['salary_pool'])/(salary_breakdown['Java']['count_processed']))
        if salary_breakdown['JavaScript']['count_processed'] !=0:
            avg_salary_js = int((salary_breakdown['JavaScript']['salary_pool'])/(salary_breakdown['JavaScript']['count_processed']))

        hh_vacancies_salary = (
            ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
            ('Python', salary_breakdown['Python']['count'], salary_breakdown['Python']['count_processed'], avg_salary_python),
            ('Java', salary_breakdown['Java']['count'], salary_breakdown['Java']['count_processed'], avg_salary_java),
            ('JavaScript', salary_breakdown['JavaScript']['count'], salary_breakdown['JavaScript']['count_processed'], avg_salary_js)
        )

    return hh_vacancies_salary


def predict_rub_salary(currency=None, salary_from=None, salary_to=None):

    if currency == 'rub' or currency == 'RUR':
        if salary_from and salary_to:
            return (salary_from + salary_to)/2
        elif salary_from and not salary_to:
            return salary_from*1.2
        elif not salary_from and salary_to:
            return salary_to*0.8
        else:
            return None
    else:
        return None


def fetch_all_vacancies_sj(sj_client_id, sj_api_key):

    sj_page_counter = 0
    sj_all_vacancies = {}
    headers = {
        'client_id': sj_client_id,
        'X-Api-App-Id': sj_api_key,
    }
    params = {
        'town': '4',
        'catalogues': '48',
        'page': {sj_page_counter},
        'count': '100'
    }
    url = 'https://api.superjob.ru/2.0/vacancies/'

    sj_one_page_vacancies = requests.get(url, headers=headers, params=params, timeout=30)
    sj_all_vacancies.update(sj_one_page_vacancies.json())

    pages_qty = int(sj_all_vacancies['total'])//int(params['count'])
    
    count = 0
    count_processed = 0
    salary_pool = 0

    salary_breakdown = {
        'Python': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        },
        'Java': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        },
        'JavaScript': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool
        }
    }

    language_pool = ['Python', 'Java', 'JavaScript']
    avg_salary_python = 0
    avg_salary_java = 0
    avg_salary_js = 0

    for language in language_pool:
        for sj_page_counter in range(0, pages_qty + 1):
            params['page'] = sj_page_counter
            sj_one_page_vacancies = requests.get(url, headers=headers, params=params, timeout=30)
            sj_all_vacancies.update(sj_one_page_vacancies.json())
            
            for vacancy in range(0, len(sj_all_vacancies['objects'])):

                if language in sj_all_vacancies['objects'][vacancy]["profession"]:
                    
                    salary_breakdown[language]['count'] += 1

                    currency = sj_all_vacancies['objects'][vacancy]["currency"]
                    salary_from = sj_all_vacancies['objects'][vacancy]["payment_from"]
                    salary_to = sj_all_vacancies['objects'][vacancy]["payment_to"]

                    if currency == 'rub' and (salary_from or salary_to):
                        salary_breakdown[language]['count_processed'] += 1
                        salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))

               
        if salary_breakdown['Python']['count_processed'] != 0:
            avg_salary_python = int((salary_breakdown['Python']['salary_pool'])/(salary_breakdown['Python']['count_processed']))
        if salary_breakdown['Java']['count_processed'] != 0:
            avg_salary_java = int((salary_breakdown['Java']['salary_pool'])/(salary_breakdown['Java']['count_processed']))
        if salary_breakdown['JavaScript']['count_processed'] !=0:
            avg_salary_js = int((salary_breakdown['JavaScript']['salary_pool'])/(salary_breakdown['JavaScript']['count_processed']))

        sj_vacancies_salary = (
            ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
            ('Python', salary_breakdown['Python']['count'], salary_breakdown['Python']['count_processed'], avg_salary_python),
            ('Java', salary_breakdown['Java']['count'], salary_breakdown['Java']['count_processed'], avg_salary_java),
            ('JavaScript', salary_breakdown['JavaScript']['count'], salary_breakdown['JavaScript']['count_processed'], avg_salary_js)
        )

    return sj_vacancies_salary


def show_table(title, table_data):
    TABLE_DATA = table_data
    table_instance = AsciiTable(TABLE_DATA, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


def main():

    load_dotenv()

    sj_client_id = os.environ['SJ_CLIENT_ID']
    sj_api_key = os.environ['SJ_API_KEY']

    show_table('HeadHunter for Moscow', fetch_all_vacancies_hh())
    show_table('SuperJob for Moscow', fetch_all_vacancies_sj(str(sj_client_id), sj_api_key))


if __name__ == '__main__':
    main()
