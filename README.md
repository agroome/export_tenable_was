# export_tenable_was
Example CLI tool showing how to export tenable web app finding

## Installation

It is recommended to create a python virtual environment to install and run this program.

1. Create a file named .env in the program directory containing your Tenable.io API keys.

```
TIO_ACCESS_KEY=012abc...
TIO_SECRET_KEY=abc012...
```

2. Install required python modules
```
$ pip install -r ./requirements.txt

```

## Usage
```
(venv)$ python ./export_was_findings.py --help
usage: export_was_findings.py [-h] -f FILENAME [-o {csv,json}] -a ASSET_LIST

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        output filenamme
  -o {csv,json}, --output-format {csv,json}
                        output format, defaults to csv
  -a ASSET_LIST, --asset-list ASSET_LIST
                        comma separated list for asset filter
```

### Example comand
```
(venv)$ python ./export_was_findings.py -f output_file -a www.example.com,support.example.com
```

### Tenable API Calls Used
This program uses the following API calls:
- Create an export: 

  [https://developer.tenable.com/reference/io-v3-uw-exports-create](https://developer.tenable.com/reference/io-v3-uw-exports-create)

  This example uses an asset filter to specify the exported findings. See the link above for additional filtering capability. Returns a job id that is use to get details (i.e. export status) and then request a download.

- Get export job details

  [https://developer.tenable.com/reference/io-v3-uw-exports-details](https://developer.tenable.com/reference/io-v3-uw-exports-details)


- Download export

  [https://developer.tenable.com/reference/io-v3-uw-exports-download](https://developer.tenable.com/reference/io-v3-uw-exports-download)


- Delete export job (after download)

  [https://developer.tenable.com/reference/io-v3-uw-exports-delete](https://developer.tenable.com/reference/io-v3-uw-exports-delete)