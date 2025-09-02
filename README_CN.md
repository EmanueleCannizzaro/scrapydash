[:abc: English](./README.md) | :mahjong: 简体中文

# ScrapydWeb：用于 Scrapyd 集群管理的 web 应用，支持 Scrapy 日志分析和可视化。

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
### :book: 推荐阅读
[:link: 如何简单高效地部署和监控分布式爬虫项目](https://github.com/EmanueleCannizzaro0/files/blob/master/scrapydash/README_CN.md)

[:link: 如何免费创建云端爬虫集群](https://github.com/EmanueleCannizzaro0/scrapyd-cluster-on-heroku/blob/master/README_CN.md)


## :eyes: 在线体验
[:link: scrapydash.herokuapp.com](https://scrapydash.herokuapp.com)


## :star: 功能特性
<details>
<summary>查看内容</summary>

- :diamond_shape_with_a_dot_inside: Scrapyd 集群管理
  - :100: 支持所有 Scrapyd JSON API
  - :ballot_box_with_check: 支持通过分组和过滤来选择若干个节点
  - :computer_mouse: **一次操作, 批量执行**

- :mag: Scrapy 日志分析
  - :1234: 数据统计
  - :chart_with_upwards_trend: **进度可视化**
  - :bookmark_tabs: 日志分类

- :battery: 增强功能
  - :package: **自动打包项目**
  - :male_detective: **集成 [:link: *LogParser*](https://github.com/EmanueleCannizzaro0/logparser)**
  - :alarm_clock: **定时器任务**
  - :e-mail: **监控和警报**
  - :iphone: 移动端 UI
  - :closed_lock_with_key: web UI 支持基本身份认证

</details>


## :computer: 上手
<details>
<summary>查看内容</summary>

### :warning: 环境要求
:heavy_exclamation_mark: **请先确保所有主机都已经安装和启动 [:link: Scrapyd](https://github.com/scrapy/scrapyd) 。**

:bangbang: 如果需要远程访问 Scrapyd，则需在 [:link: Scrapyd 配置文件](https://scrapyd.readthedocs.io/en/latest/config.html#example-configuration-file)
中设置 'bind_address = 0.0.0.0'，然后重启 Scrapyd。

### :arrow_down: 安装
- 通过 pip:
```bash
pip install scrapydash
```
:heavy_exclamation_mark: 如果 pip 安装结果不是最新版本的 scrapydash，请先执行`python -m pip install --upgrade pip`，或者前往 https://pypi.org/project/scrapydash/#files 下载 tar.gz 文件并执行安装命令 `pip install scrapydash-x.x.x.tar.gz`

- 通过 git:
```bash
pip install --upgrade git+https://github.com/EmanueleCannizzaro0/scrapydash.git
```
或:
```bash
git clone https://github.com/EmanueleCannizzaro0/scrapydash.git
cd scrapydash
python setup.py install
```

### :arrow_forward: 启动
1. 通过运行命令 `scrapydash` 启动 ScrapydWeb（首次启动将自动生成配置文件）。
2. 访问 http://127.0.0.1:5000 **（建议使用 Google Chrome 以获取更好体验）**。

### :globe_with_meridians: 浏览器支持
最新版本的 Google Chrome，Firefox 和 Safari。

</details>


## :heavy_check_mark: 执行测试
<details>
<summary>查看内容</summary>

<br>

```bash
$ git clone https://github.com/EmanueleCannizzaro0/scrapydash.git
$ cd scrapydash

# 创建虚拟环境
$ pip install virtualenv
$ virtualenv venv/scrapydash
# 亦可指定 Python 解释器：$ virtualenv -p /usr/local/bin/python3.7 venv/scrapydash
$ source venv/scrapydash/bin/activate

# 安装依赖库
(scrapydash) $ python setup.py install
(scrapydash) $ pip install pytest
(scrapydash) $ pip install coverage

# 请先确保已经安装和启动 Scrapyd，然后检查和更新 tests/conftest.py 文件中的 custom_settings
(scrapydash) $ vi tests/conftest.py
(scrapydash) $ curl http://127.0.0.1:6800

# '-x': 在第一次出现失败时停止测试
(scrapydash) $ coverage run --source=scrapydash -m pytest tests/test_a_factory.py -s -vv -x
(scrapydash) $ coverage run --source=scrapydash -m pytest tests -s -vv --disable-warnings
(scrapydash) $ coverage report
# 生成 HTML 报告, 文件位于 htmlcov/index.html
(scrapydash) $ coverage html
```

</details>


## :building_construction: 框架和依赖库
<details>
<summary>查看内容</summary>

<br>

- 前端
  - [:link: Element](https://github.com/ElemeFE/element)
  - [:link: ECharts](https://github.com/apache/incubator-echarts)
- 后端
  - [:link: Flask](https://github.com/pallets/flask)

</details>


## :clipboard: 更新日志
详见 [:link: HISTORY.md](./HISTORY.md)。


## :man_technologist: 作者
| [<img src="https://github.com/EmanueleCannizzaro0.png" width="100px;"/>](https://github.com/EmanueleCannizzaro0)<br/> [<sub>EmanueleCannizzaro0</sub>](https://github.com/EmanueleCannizzaro0) |
| --- |


## :busts_in_silhouette: 贡献者
| [<img src="https://github.com/simplety.png" width="100px;"/>](https://github.com/simplety)<br/> [<sub>Kaisla</sub>](https://github.com/simplety) |
| --- |


## :copyright: 软件许可
本项目采用 GNU General Public License v3.0 许可协议，详见 [:link: LICENSE](./LICENSE)。
