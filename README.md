# Wikipedia Scraping Demo

This Wikipedia URL lists most if not all of the mainstream programming languages: https://en.wikipedia.org/wiki/List_of_programming_languages. Scrape this page and extract all the links to individual programming languages from it, storing the HTML of each page in a manner where they can be easily accessed again, including being able to determine which URL the HTML came from. After you have scraped every programming language page, parse each page of HTML looking for the following values from the infobox (box on the top right side of some articles): paradigm, first appeared, and file extensions. These values will not appear on every page. If a page has all three values present (ex. infobox here https://en.wikipedia.org/wiki/Python_(programming_language)), add it to a structured output file (JSON, CSV).

A record in the output file should contain:
* the name of the language (from the URL is fine)
* the three values from the infobox
* the number of header sections in the HTML (sections of the article with an underline separator)
* the number of urls/links to other wikipedia articles present in the article itself (not the whole page)

The final output file should only contain records/rows for pages that have all specified infobox values present.

## To Run

Setup Environment
----

Create and enter a python virtual environment.
Install necessary dependencies for the script.

```bash
python3 -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
```

Run
----

Create and enter a directory to contain output files.
Run the script, capturing stdout in a log file.

```bash
mkdir output
cd output
python ../wikiscrape.py -c > stdout.log
```

Running the script will produce a file `index.json` containing a JSON blob of all languages captured, and a directory containing the webpages that the script visited.
