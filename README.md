# Tennis_Visualisation

# Setup (windows):

## Install python3
- Install python3 and then install pip. Once the installation is complete install the virtualenv
```bash
$ pip install virtualenv
```
- Once the virtualenv is installed create a virtual environment in this folder as follows
```bash
$ python3 -m virtualenv venv
		or
$ python3 -m venv venv
```
- Activate the virtual environment as follows
windows - cmd
```bash
$ .\venv\Scripts\activate
```
Linux or Mac
```bash
$ source venv/bin/activate
```
- Install the required packages using requirements.txt
```bash
$ pip install -r requirements.txt
```

Change the paths in scrapper.py files for sample_tennis_data_table.csv file.
Also change any other paths pointing to local folders.

<b> How to run the project </b>
- Download the elastic search https://www.elastic.co/downloads/elasticsearch choosing required platform.
- Run elastic search using the command .\bin\elasticsearch.bat
- Run app.py and tennis.py files in two separate terminals
- To scrape the data run scrapper.py file with specified arguments and view the website that is running in localhost. example:http://127.0.0.1:8080/ 

To scrape live matches, command is "python src\scrappper.py --live" and for finished matches 
	"python src\scrapper.py --finished --from_date 2021-02-03 --to_date 2021-02-04"
Run app.py and tennis.py
