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
    language = ''
    publish_date_from = datetime.datetime.now() - datetime.timedelta(90)
    params = {
        'text': f'{language}',
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
    response.raise_for_status()
    pages_qty = vacancies['pages']
    hh_all_vacancies = {}

    count = 0
    count_processed = 0
    salary_pool = 0
    avg_salary = 0

    salary_breakdown = {
        'Python': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        },
        'Java': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        },
        'JavaScript': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        }
    }

    language_pool = ['Python', 'Java', 'JavaScript']

    for language in language_pool:

        for page in range(0, pages_qty):

            params['text'] = language
            params['page'] = page
            one_page_vacancies = requests.get(url, params=params)
            hh_all_vacancies.update(one_page_vacancies.json())
            one_page_vacancies.raise_for_status()

            for vacancy_id, vacancy in enumerate(hh_all_vacancies['items']):

                salary_breakdown[language]['count'] += 1

                if hh_all_vacancies['items'][vacancy_id]['salary'] and hh_all_vacancies['items'][vacancy_id]['salary']['currency'] == 'RUR':
                    currency = hh_all_vacancies['items'][vacancy_id]['salary']['currency']
                    salary_from = hh_all_vacancies['items'][vacancy_id]['salary']['from']
                    salary_to = hh_all_vacancies['items'][vacancy_id]['salary']['to']
                    salary_breakdown[language]['count_processed'] += 1
                    salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))

        if salary_breakdown[language]['count_processed'] != 0:
            salary_breakdown[language]['avg_salary'] = int((salary_breakdown[language]['salary_pool'])/(salary_breakdown[language]['count_processed']))
        else:
            salary_breakdown[language]['avg_salary'] = "N/A"

        hh_vacancies_salary = (
            ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
            ('Python', salary_breakdown['Python']['count'], salary_breakdown['Python']['count_processed'], salary_breakdown['Python']['avg_salary']),
            ('Java', salary_breakdown['Java']['count'], salary_breakdown['Java']['count_processed'], salary_breakdown['Java']['avg_salary']),
            ('JavaScript', salary_breakdown['JavaScript']['count'], salary_breakdown['JavaScript']['count_processed'], salary_breakdown['JavaScript']['avg_salary'])
        )

    return hh_vacancies_salary


def predict_rub_salary(currency=None, salary_from=None, salary_to=None):

    if currency not in ['rub', 'RUR']:
        return None
    else:
        if salary_from and salary_to:
            return (salary_from + salary_to)/2
        elif salary_from:
            return salary_from*1.2
        else:
            return salary_to*0.8


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
    sj_one_page_vacancies.raise_for_status()

    pages_qty = int(sj_all_vacancies['total'])//int(params['count'])

    count = 0
    count_processed = 0
    salary_pool = 0
    avg_salary = 0

    salary_breakdown = {
        'Python': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        },
        'Java': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        },
        'JavaScript': {
            'count': count,
            'count_processed': count_processed,
            'salary_pool': salary_pool,
            'avg_salary': avg_salary
        }
    }

    language_pool = ['Python', 'Java', 'JavaScript']

    for language in language_pool:
        for sj_page_counter in range(0, pages_qty + 1):
            params['page'] = sj_page_counter
            sj_one_page_vacancies = requests.get(url, headers=headers, params=params, timeout=30)
            sj_all_vacancies.update(sj_one_page_vacancies.json())
            sj_one_page_vacancies.raise_for_status()

            for vacancy_id, vacancy in enumerate(sj_all_vacancies['objects']):

                if language in sj_all_vacancies['objects'][vacancy_id]["profession"]:

                    salary_breakdown[language]['count'] += 1

                    currency = sj_all_vacancies['objects'][vacancy_id]["currency"]
                    salary_from = sj_all_vacancies['objects'][vacancy_id]["payment_from"]
                    salary_to = sj_all_vacancies['objects'][vacancy_id]["payment_to"]

                    if currency == 'rub' and (salary_from or salary_to):
                        salary_breakdown[language]['count_processed'] += 1
                        salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))

        if salary_breakdown[language]['count_processed'] != 0:
            salary_breakdown[language]['avg_salary'] = int((salary_breakdown[language]['salary_pool'])/(salary_breakdown[language]['count_processed']))
        else:
            salary_breakdown[language]['avg_salary'] = "N/A"

        sj_vacancies_salary = (
            ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
            ('Python', salary_breakdown['Python']['count'], salary_breakdown['Python']['count_processed'], salary_breakdown['Python']['avg_salary']),
            ('Java', salary_breakdown['Java']['count'], salary_breakdown['Java']['count_processed'], salary_breakdown['Java']['avg_salary']),
            ('JavaScript', salary_breakdown['JavaScript']['count'], salary_breakdown['JavaScript']['count_processed'], salary_breakdown['JavaScript']['avg_salary'])
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
    show_table('SuperJob for Moscow', fetch_all_vacancies_sj(sj_client_id, sj_api_key))


if __name__ == '__main__':
    main()
