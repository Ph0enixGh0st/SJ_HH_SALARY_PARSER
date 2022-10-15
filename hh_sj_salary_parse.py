import datetime
import json
import os
import requests

from datetime import timedelta as tdelta
from dotenv import load_dotenv
from terminaltables import AsciiTable


def fetch_all_vacancies_hh():

    salary_breakdown = {}
    language_pool = ['Python', 'Java', 'JavaScript']
    labels_pool = {
        'count': 0,
        'count_processed': 0,
        'salary_pool': 0,
        'avg_salary': 0
    }

    for language in language_pool:
        salary_breakdown[language] = dict(labels_pool)

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
    hh_all_vacancies = {}

    for language in salary_breakdown:

        page = 0
        pages = 1

        while page <= pages:

            params['text'] = language
            params['page'] = page
            one_page_vacancies = requests.get(url, params=params)
            one_page_vacancies.raise_for_status()
            hh_all_vacancies.update(one_page_vacancies.json())
            pages = hh_all_vacancies['pages']

            for vacancy in hh_all_vacancies['items']:

                salary_breakdown[language]['count'] += 1

                if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
                    currency = vacancy['salary']['currency']
                    salary_from = vacancy['salary']['from']
                    salary_to = vacancy['salary']['to']
                    salary_breakdown[language]['count_processed'] += 1
                    salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))
            page += 1

        if salary_breakdown[language]['count_processed']:
            salary_breakdown[language]['avg_salary'] = int((salary_breakdown[language]['salary_pool'])/(salary_breakdown[language]['count_processed']))
        else:
            salary_breakdown[language]['avg_salary'] = "N/A"

        hh_vacancies_salary = (('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),)

        for language in language_pool:

            hh_vacancies_salary = hh_vacancies_salary + ((language, salary_breakdown[language]['count'], salary_breakdown[language]['count_processed'], salary_breakdown[language]['avg_salary']),)

    return hh_vacancies_salary


def predict_rub_salary(currency=None, salary_from=None, salary_to=None):

    if currency in ['rub', 'RUR']:
        if salary_from and salary_to:
            return (salary_from + salary_to)/2
        elif salary_from:
            return salary_from*1.2
        return salary_to*0.8
    else:
        return None


def fetch_all_vacancies_sj(sj_client_id, sj_api_key):

    sj_page_counter = 0
    sj_all_vacancies = {}
    language = ''
    headers = {
        'client_id': sj_client_id,
        'X-Api-App-Id': sj_api_key,
    }
    params = {
        'town': '4',
        'catalogues': '48',
        'page': {sj_page_counter},
        'count': '100',
        'no_agreement': '1',
        'keyword': f'{language}'
    }
    url = 'https://api.superjob.ru/2.0/vacancies/'

    salary_breakdown = {}
    language_pool = ['Python', 'Java', 'JavaScript']
    labels_pool = {
        'count': 0,
        'count_processed': 0,
        'salary_pool': 0,
        'avg_salary': 0
    }

    for language in language_pool:
        salary_breakdown[language] = dict(labels_pool)

    for language in salary_breakdown:

        sj_page_counter = 0
        pages = 1

        while sj_page_counter <= pages + 1:

            params['page'] = sj_page_counter
            params['keyword'] = language
            sj_one_page_vacancies = requests.get(url, headers=headers, params=params, timeout=30)
            sj_one_page_vacancies.raise_for_status()
            sj_all_vacancies.update(sj_one_page_vacancies.json())
            pages = int(sj_all_vacancies['total'])//int(params['count'])

            for vacancy in sj_all_vacancies['objects']:

                salary_breakdown[language]['count'] += 1

                currency = vacancy['currency']
                salary_from = vacancy['payment_from']
                salary_to = vacancy['payment_to']

                if currency == 'rub' and (salary_from or salary_to):
                    salary_breakdown[language]['count_processed'] += 1
                    salary_breakdown[language]['salary_pool'] += int(predict_rub_salary(currency, salary_from, salary_to))
            sj_page_counter += 1

        if salary_breakdown[language]['count_processed']:
            salary_breakdown[language]['avg_salary'] = int((salary_breakdown[language]['salary_pool'])/(salary_breakdown[language]['count_processed']))
        else:
            salary_breakdown[language]['avg_salary'] = 'N/A'

        sj_vacancies_salary = (('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),)

        for language in language_pool:

            sj_vacancies_salary = sj_vacancies_salary + ((language, salary_breakdown[language]['count'], salary_breakdown[language]['count_processed'], salary_breakdown[language]['avg_salary']),)

    return sj_vacancies_salary


def show_table(title, table_data):
    table_instance = AsciiTable(table_data, title)
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
