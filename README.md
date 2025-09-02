:abc: English | [:mahjong: 简体中文](https://github.com/EmanueleCannizzaro0/scrapydash/blob/master/README_CN.md)

# ScrapydWeb: Web app for Scrapyd cluster management, with support for Scrapy log analysis & visualization.

[![PyPI - scrapydash Version](https://img.shields.io/pypi/v/scrapydash.svg)](https://pypi.org/project/scrapydash/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scrapydash.svg)](https://pypi.org/project/scrapydash/)
[![CircleCI](https://circleci.com/gh/EmanueleCannizzaro0/scrapydash/tree/master.svg?style=shield)](https://circleci.com/gh/EmanueleCannizzaro0/scrapydash/tree/master)
[![codecov](https://codecov.io/gh/EmanueleCannizzaro0/scrapydash/branch/master/graph/badge.svg)](https://codecov.io/gh/EmanueleCannizzaro0/scrapydash)
[![Coverage Status](https://coveralls.io/repos/github/EmanueleCannizzaro0/scrapydash/badge.svg?branch=master)](https://coveralls.io/github/EmanueleCannizzaro0/scrapydash?branch=master)
[![Downloads - total](https://static.pepy.tech/badge/scrapydash)](https://pepy.tech/project/scrapydash)
[![GitHub license](https://img.shields.io/github/license/EmanueleCannizzaro0/scrapydash.svg)](https://github.com/EmanueleCannizzaro0/scrapydash/blob/master/LICENSE)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/EmanueleCannizzaro0/scrapydash.svg?style=social)](https://twitter.com/intent/tweet?text=@EmanueleCannizzaro0_%20ScrapydWeb:%20Web%20app%20for%20Scrapyd%20cluster%20management,%20with%20support%20for%20Scrapy%20log%20analysis%20%26%20visualization.%20%23python%20%23scrapy%20%23scrapyd%20%23webscraping%20%23scrapydash%20&url=https%3A%2F%2Fgithub.com%2FEmanueleCannizzaro0%2Fscrapydash)


##
![servers](https://raw.githubusercontent.com/EmanueleCannizzaro0/scrapydash/master/screenshots/servers.png)

## Scrapyd :x: ScrapydWeb :x: LogParser
### :book: Recommended Reading
[:link: How to efficiently manage your distributed web scraping projects](https://github.com/EmanueleCannizzaro0/files/blob/master/scrapydash/README.md)

[:link: How to set up Scrapyd cluster on Heroku](https://github.com/EmanueleCannizzaro0/scrapyd-cluster-on-heroku)


## :eyes: Demo
[:link: scrapydash.herokuapp.com](https://scrapydash.herokuapp.com)


## :rocket: Sponsor
This project is supported by [IPRoyal](https://iproyal.com/?r=802099). You can get premium quality proxies at unbeatable prices
with a discount using [this referral link](https://iproyal.com/?r=802099)!


## :stars: Features
<details>
<summary>View contents</summary>

- :diamond_shape_with_a_dot_inside: Scrapyd Cluster Management
  - :100: All Scrapyd JSON API Supported
  - :ballot_box_with_check: Group, filter and select any number of nodes
  - :computer_mouse: **Execute command on multinodes with just a few clicks**

- :mag: Scrapy Log Analysis
  - :bar_chart: Stats collection
  - :chart_with_upwards_trend: **Progress visualization**
  - :bookmark_tabs: Logs categorization

- :battery: Enhancements
  - :package: **Auto packaging**
  - :male_detective: **Integrated with [:link: *LogParser*](https://github.com/EmanueleCannizzaro0/logparser)**
  - :alarm_clock: **Timer tasks**
  - :e-mail: **Monitor & Alert**
  - :iphone: Mobile UI
  - :closed_lock_with_key: Basic auth for web UI

</details>


## :computer: Getting Started
<details>
<summary>View contents</summary>

### :warning: Prerequisites
:heavy_exclamation_mark: **Make sure that [:link: Scrapyd](https://github.com/scrapy/scrapyd) has been installed and started on all of your hosts.**

:bangbang: Note that for remote access, you have to manually set 'bind_address = 0.0.0.0' in [:link: the configuration file of Scrapyd](https://scrapyd.readthedocs.io/en/latest/config.html#example-configuration-file)
and restart Scrapyd to make it visible externally.

### :arrow_down: Install
- Use pip:
```bash
pip install scrapydash
```
:heavy_exclamation_mark: Note that you may need to execute `python -m pip install --upgrade pip` first in order to get the latest version of scrapydash, or download the tar.gz file from https://pypi.org/project/scrapydash/#files and get it installed via `pip install scrapydash-x.x.x.tar.gz`

- Use git:
```bash
pip install --upgrade git+https://github.com/EmanueleCannizzaro0/scrapydash.git
```
Or:
```bash
git clone https://github.com/EmanueleCannizzaro0/scrapydash.git
cd scrapydash
python setup.py install
```

### :arrow_forward: Start
1. Start ScrapydWeb via command `scrapydash`. (a config file would be generated for customizing settings at the first startup.)
2. Visit http://127.0.0.1:5000 **(It's recommended to use Google Chrome for a better experience.)**

### :globe_with_meridians: Browser Support
The latest version of Google Chrome, Firefox, and Safari.

</details>


## :heavy_check_mark: Running the tests
<details>
<summary>View contents</summary>

<br>

```bash
$ git clone https://github.com/EmanueleCannizzaro0/scrapydash.git
$ cd scrapydash

# To create isolated Python environments
$ pip install virtualenv
$ virtualenv venv/scrapydash
# Or specify your Python interpreter: $ virtualenv -p /usr/local/bin/python3.7 venv/scrapydash
$ source venv/scrapydash/bin/activate

# Install dependent libraries
(scrapydash) $ python setup.py install
(scrapydash) $ pip install pytest
(scrapydash) $ pip install coverage

# Make sure Scrapyd has been installed and started, then update the custom_settings item in tests/conftest.py
(scrapydash) $ vi tests/conftest.py
(scrapydash) $ curl http://127.0.0.1:6800

# '-x': stop on first failure
(scrapydash) $ coverage run --source=scrapydash -m pytest tests/test_a_factory.py -s -vv -x
(scrapydash) $ coverage run --source=scrapydash -m pytest tests -s -vv --disable-warnings
(scrapydash) $ coverage report
# To create an HTML report, check out htmlcov/index.html
(scrapydash) $ coverage html
```

</details>


## :building_construction: Built With
<details>
<summary>View contents</summary>

<br>

- Front End
  - [:link: Element](https://github.com/ElemeFE/element)
  - [:link: ECharts](https://github.com/apache/incubator-echarts)

- Back End
  - [:link: Flask](https://github.com/pallets/flask)

</details>


## :clipboard: Changelog
Detailed changes for each release are documented in the [:link: HISTORY.md](https://github.com/EmanueleCannizzaro0/scrapydash/blob/master/HISTORY.md).


## :man_technologist: Author
| [<img src="https://github.com/EmanueleCannizzaro0.png" width="100px;"/>](https://github.com/EmanueleCannizzaro0)<br/> [<sub>EmanueleCannizzaro0</sub>](https://github.com/EmanueleCannizzaro0) |
| --- |


## :busts_in_silhouette: Contributors
| [<img src="https://github.com/simplety.png" width="100px;"/>](https://github.com/simplety)<br/> [<sub>Kaisla</sub>](https://github.com/simplety) |
| --- |


## :copyright: License
This project is licensed under the GNU General Public License v3.0 - see the [:link: LICENSE](https://github.com/EmanueleCannizzaro0/scrapydash/blob/master/LICENSE) file for details.


## :star: Stargazers over time
[![Stargazers over time](https://starchart.cc/EmanueleCannizzaro0/scrapydash.svg?variant=adaptive)](https://starchart.cc/EmanueleCannizzaro0/scrapydash)
