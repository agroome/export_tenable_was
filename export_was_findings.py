import os
import requests
import argparse
from time import sleep
from dotenv import load_dotenv
from pprint import pprint

export_url = 'https://cloud.tenable.com/api/v3/exports/jobs'

POLL_INTERVAL_SECONDS = 2
DEFAULT_SEVERITY = (0, 1, 2, 3, 4)
DEFAULT_STATE = ['ACTIVE', 'RESURFACED', 'NEW']
WAS_FIELDS = (
    'severity',
    'definition.name',
    'definition.id',
    'definition.family',
    'state',
    'first_observed',
    'last_observed',
    'finding_id',
    'definition.patch_published',
    'definition.description',
    'definition.solution',
    'definition.see_also',
    'definition.vulnerability_published',
    'definition.plugin_published',
    'definition.plugin_updated',
    'definition.cvss2.base_score',
    'definition.cvss2.base_vector',
    'definition.cvss3.base_score',
    'definition.cvss3.base_vector',
    'definition.references',
    'output',
    'risk_modified',
    'asset.name',
    'asset.id',
    'definition.severity'
)

load_dotenv()

access_key = os.getenv('TIO_ACCESS_KEY')
secret_key = os.getenv('TIO_SECRET_KEY')

x_api_keys = f'accessKey={access_key};secretKey={secret_key}'
get_headers = {
    'Accept': 'application/json',
    'X-ApiKeys': f'accessKey={access_key};secretKey={secret_key}'
}
post_headers = {**get_headers, **{'Content-type': 'application/json'}}
    

def search_export_jobs():
    search_jobs_url = f'{export_url}/search'
    payload = {'limit': 200}
    response = requests.post(search_jobs_url, headers=post_headers, json=payload)
    return response.json()['exports']


def get_export_details(job_id):
    get_details_url = f'{export_url}/{job_id}'
    response = requests.get(get_details_url, headers=get_headers)
    return response.json()['export_details']


def delete_export_job(job_id):
    delete_job_url = f'{export_url}/{job_id}'
    requests.delete(delete_job_url, headers=get_headers)


# def list_export_jobs():
#     jobs = search_export_jobs()
#     for job in jobs:
#         pprint(get_export_details(job['job_uuid']))


# def delete_export_jobs():
#     jobs = search_export_jobs()
#     for job in jobs:
#         print(f'DELETING JOB: {job}')
#         delete_export_job(job['job_uuid'])


def download_job(job_details):
    filename = job_details['filename']
    job_id = job_details["job_uuid"]
    download_url = f'https://cloud.tenable.com/api/v3/exports/jobs/{job_id}/content'
    headers = {
        "Accept": "application/octet-stream",
        "X-ApiKeys": x_api_keys
    }
    response = requests.get(download_url, headers=headers)
    with open(filename, 'w') as fp:
        fp.write(response.text)



def export_was_findings(asset_names, filename, format='csv', fields=WAS_FIELDS, severity=DEFAULT_SEVERITY, state=DEFAULT_STATE):
    payload = {
        'definition': {
            'fields': list(fields), 
            'filter': {
                'and': [
                    {'operator': 'eq', 'property': 'severity', 'value': list(severity)}, 
                    {'operator': 'eq', 'property': 'state', 'value': list(state)}, 
                    {'operator': 'eq', 'property': 'asset.name', 'value': asset_names}, 
                ]
            }
        },
        'expiration': 2,
        'format': format,
        'name': filename,
        'source': 'findings/vulnerabilities/webapp'
    }

    results = requests.post(export_url, headers=post_headers, json=payload)
    if results.ok:
        job_id = results.json()['id']
    
        while True:
            job_details = get_export_details(job_id)
            if job_details['job_status'] != 'running':
                break
            sleep(POLL_INTERVAL_SECONDS)
    
    
        if job_details['job_status'] != 'complete':
            print(f"downloading {job_details['filename']}")
            download_job(job_details)
            print(f"download complete.")
        else:
            print(f'export status: {job_details["job_status"]}')
    
        delete_export_job(job_id)
    else:
        print(f'{results.status_code}: {results.reason}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', required=True, help='output filenamme')
    parser.add_argument('-o', '--output-format', choices=['csv', 'json'], default='csv', help='output format, defaults to csv')
    parser.add_argument('-a', '--asset-list', required=True, help='comma separated list for asset filter')

    args = parser.parse_args()
    asset_list = args.asset_list.replace(' ', '').split(',')

    print(f'export assets to {args.output_format}: {asset_list}')

    export_was_findings(asset_list, args.filename, args.output_format)


if __name__=='__main__':
    main()
