
import datetime
import json
import os
import requests

from dataclasses import dataclass
from datetime import timedelta as tdelta
from dotenv import load_dotenv
from django.utils import timezone
from terminaltables import AsciiTable


def fetch_all_vacancies_hh():
    city_id = '1'
    specialization = '1'
    publish_date_from = datetime.datetime.now() - datetime.timedelta(90)
    params = {
        'area': city_id,
        'page': 0,
        'per_page': 100,
        'specialization': specialization,
        'date_from': publish_date_from.strftime('%Y-%m-%d')
    }
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=params)
    vacancies = response.json()
    pages_qty = int(vacancies.get('pages'))
    all_vacancies = {}

    with open('hh_all_vacancies.json', 'w', encoding='utf-8') as file:
        for page in range(0, pages_qty-1):
            params['page'] = page
            one_page_vacancies = requests.get(url, params=params)
            all_vacancies.update(one_page_vacancies.json())
            json.dump(all_vacancies, file, indent=4, ensure_ascii=False)


def read_json_file(file):
    with open(file, 'r', encoding='utf-8') as json_fix:
        response = json_fix.read()
        response = response.replace('\n', '')
        response = response.replace('}{', '},{')
        response = '[' + response + ']'
        return json.loads(response)


def count_prog_langs_hh(pages_qty=20, file_name='hh_all_vacancies.json'):
    hh_all_vacancies = read_json_file(file_name)

    python_count = 0
    js_count = 0
    java_count = 0

    python_count_processed = 0
    python_salary_pool = 0
    js_count_processed = 0

    js_salary_pool = 0
    java_count_processed = 0
    java_salary_pool = 0

    for page in range(0, pages_qty-1):
        for vacancy_id in range(0, 99):
            if 'Python' in hh_all_vacancies[page]['items'][vacancy_id]['name']:
                python_count += 1
                if predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']):
                    python_count_processed += 1
                    python_salary_pool = python_salary_pool + int(predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']))

            if 'Java' in hh_all_vacancies[page]['items'][vacancy_id]['name']:
                java_count += 1
                if predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']):
                    java_count_processed += 1
                    java_salary_pool = java_salary_pool + int(predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']))

            if 'JavaScript' in hh_all_vacancies[page]['items'][vacancy_id]['name']:
                js_count += 1
                if predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']):
                    js_count_processed += 1
                    js_salary_pool = js_salary_pool + int(predict_rub_salary_hh(hh_all_vacancies[page]['items'][vacancy_id]['id']))

    avg_salary_python = int(python_salary_pool/python_count_processed)
    avg_salary_java = int(java_salary_pool/java_count_processed)
    avg_salary_js = int(js_salary_pool/js_count_processed)

    TABLE_DATA = (
        ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
        ('Python', python_count, python_count_processed, avg_salary_python),
        ('Java', java_count, java_count_processed, avg_salary_java),
        ('JavaScript', js_count, js_count_processed, avg_salary_js)
        )

    return TABLE_DATA


def predict_rub_salary_hh(id):

    url = f'https://api.hh.ru/vacancies/{id}'
    hh_id_salary = requests.get(url)
    vacancy_info = hh_id_salary.json()

    if vacancy_info['salary']:
        if vacancy_info['salary']['currency'] != 'RUR':
            return None
        elif vacancy_info['salary']['from'] and vacancy_info['salary']['to']:
            return (vacancy_info['salary']['from'] + vacancy_info['salary']['to'])/2
        elif vacancy_info['salary']['from'] and not vacancy_info['salary']['to']:
            return (vacancy_info['salary']['from'])*1.2
        elif not vacancy_info['salary']['from'] and vacancy_info['salary']['to']:
            return (vacancy_info['salary']['to'])*0.8
        else:
            return None


def predict_rub_salary_sj(currency=None, vacancy_from=None, vacancy_to=None):

    if currency == 'rub':
        if vacancy_from and vacancy_to:
            return (vacancy_from+vacancy_to)/2
        elif vacancy_from and not vacancy_to:
            return vacancy_from*1.2
        elif not vacancy_from and vacancy_to:
            return vacancy_to*0.8
        else:
            return None
    else:
        return None


def fetch_all_vacancies_sj(client_id, api_key):

    sj_page_counter = 0
    sj_all_vacancies = {}
    headers = {
        'client_id': client_id,
        'X-Api-App-Id': api_key,
    }
    params = {
        'town': '4',
        'catalogues': '48',
        'page': {sj_page_counter},
        'count': '100'
    }
    url = 'https://api.superjob.ru/2.0/vacancies/'

    with open('sj_all_vacancies.json', 'w', encoding='utf-8') as file:
        for sj_page_counter in range(0, 4):
            params['page'] = sj_page_counter
            sj_one_page_vacancies = requests.get(url, headers=headers, params=params, timeout=30)
            sj_all_vacancies.update(sj_one_page_vacancies.json())
            json.dump(sj_all_vacancies, file, indent=4, ensure_ascii=False)


def count_prog_langs_sj(pages_qty=500, file_name='sj_all_vacancies.json'):
        sj_all_vacancies = read_json_file(file_name)

        python_count = 0
        js_count = 0
        java_count = 0

        python_count_processed = 0
        python_salary_pool = 0
        js_count_processed = 0
        js_salary_pool = 0
        java_count_processed = 0
        java_salary_pool = 0

        for page in range(0, int(sj_all_vacancies[0]['total'])//100):
            for vacancy_id in range(0, 99):

                if 'Python' in sj_all_vacancies[page]['objects'][vacancy_id]['profession']:
                    python_count += 1
                    if predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to']):
                        python_count_processed += 1
                        python_salary_pool = python_salary_pool + predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to'])

                if 'Java' in sj_all_vacancies[page]['objects'][vacancy_id]['profession']:
                    java_count += 1
                    if predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to']):
                        java_count_processed += 1
                        java_salary_pool = java_salary_pool + predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to'])

                if 'JavaScript' in sj_all_vacancies[page]['objects'][vacancy_id]['profession']:
                    js_count += 1
                    if predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to']):
                        js_count_processed += 1
                        js_salary_pool = js_salary_pool + predict_rub_salary_sj(sj_all_vacancies[page]['objects'][vacancy_id]['currency'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_from'], sj_all_vacancies[page]['objects'][vacancy_id]['payment_to'])

        if python_count_processed != 0:
            avg_salary_python = int(python_salary_pool/python_count_processed)
        else:
            avg_salary_python = 'N/A'

        if java_count_processed != 0:
            avg_salary_java = int(java_salary_pool/java_count_processed)
        else:
            avg_salary_java = 'N/A'

        if js_count_processed != 0:
            avg_salary_js = int(js_salary_pool/js_count_processed)
        else:
            avg_salary_js = 'N/A'

        TABLE_DATA = (
        ('Language', 'Vacancies_Found', 'Vacancies_Processed', 'Avg Salary'),
        ('Python', python_count, python_count_processed, avg_salary_python),
        ('Java', java_count, java_count_processed, avg_salary_java),
        ('JavaScript', js_count, js_count_processed, avg_salary_js)
        )

        return TABLE_DATA

def show_table(title, table_data):
    TABLE_DATA = table_data
    table_instance = AsciiTable(TABLE_DATA, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


def main():
    load_dotenv()

    client_id = os.environ['CLIENT_ID']
    api_key = os.environ['API_KEY']

    fetch_all_vacancies_hh()
    count_prog_langs_hh()
    fetch_all_vacancies_sj(str(client_id), api_key)
    count_prog_langs_sj()
    show_table('HeadHunter for Moscow', count_prog_langs_hh())
    show_table('SuperJob for Moscow', count_prog_langs_sj())


if __name__ == '__main__':
    main()
