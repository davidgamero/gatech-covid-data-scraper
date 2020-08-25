# Create fresh dependency package directory
rm -rf ./gatech-covid-data-lambda
mkdir gatech-covid-data-lambda

#mkdir gatech-covid-data-lambda/package

# Install dependencies
pip3 install --target ./gatech-covid-data-lambda -r requirements.txt

# Zip dependencies
#cd gatech-covid-data-lambda/package
#zip -r9 ../function.zip .

#cd ..
#rm -rf ./package

# Add scripts to lambda folder

cp ./lambda_function.py ./gatech-covid-data-lambda/lambda_function.py
cp ./scrape_covid_data.py ./gatech-covid-data-lambda/scrape_covid_data.py

# Zip the lambda folder
rm gatech-covid-data-lambda.zip

cd gatech-covid-data-lambda
zip -r9 ../gatech-covid-data-lambda.zip .