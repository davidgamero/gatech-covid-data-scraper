# 😷 GATech COVID-19 Data Scraper

## 🏁 Getting Started

```
git clone git@github.com:davidgamero/gatech-covid-data-scraper.git
cd gatech-covid-data-scraper
pip install -r requirements.txt
```

```
python scrape_covid_data.py
```
Data will be written to gatech_covid_data.csv

## ℹ️ Project Info
Q: Why did I make this?

A: I searched "gatech covid" on GitHub and only got one result which was in R by [cjwichman](https://github.com/cjwichman/gatech_covid)

I believe that pandemic health data should be freely and easily accessible and wanted to make my own plots, so I decided to make a Python scraper implementation to better understand the data.

My main improvements were automated extraction of case numbers for rows that are inconsistent in formatting ex: due to the [GATech Health Alert Site](https://health.gatech.edu/coronavirus/health-alerts)'s wildly inconsistent conventions 🤢 I used a series of Regular Expressions to parse for keywords and then extract integers using observed rules. All fuzzy extractions are printed to the command line for manual verification.

The patterns currently recognized are 
1) Rows with a 'Position' value of 'Students (N)' where N is the number of cases, which I extracted with a regex capture group for the numeric contents of the parentheses
2) Rows with a 'Position' value of 'Students' OR 'Various'. For these rows I use a regex search to find the first integer present in the 'Campus Impact' column as the number of cases. It would be nice to eventually check that there is only a single match and throw an error for manual review if there are multiple integers.

## 💾 AWS Lambda -> S3
 To deploy as an AWS Lambda function build `gatech-covid-data-lambda.zip` with `build_lambda_zip.sh` and upload to a Python Lambda with `s3:PutObject,s3:PutObjectAcl` permissions to the target bucket
```
chmod +x build_lambda_zip.sh
./build_lambda_zip.sh
```

Upload `gatech-covid-data-lambda.zip` to AWS Lambda

I recommend increasing timeout to >5s as the data size increases over time with more rows

## Acknowledgements
Shout out to [cjwichman](https://github.com/cjwichman/gatech_covid) for paving the way with their [gatech_covid](https://github.com/cjwichman/gatech_covid) repo