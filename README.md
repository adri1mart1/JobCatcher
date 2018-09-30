# JobCatcher

![JobCatcher Screenshot](https://raw.github.com/yoannsculo/JobCatcher/master/screenshots/jobcatcher.png)

JobCatcher is a daemon that retrieves job offers from multiple job boards feeds
and generates custom RSS feeds and HTML reports for you. This is a decentralized
software meant to run of your own server.

JobCatcher comes with a filter feature, so you can filter company names with
black or whitelists.

Think of it as a RSS feed reader with filter feature.

I would like this software to be under GPLv2 License. But I need to check if
this is compatible with dependencies I've choosen.

## Work in Progress

This project is a fork from https://github.com/yoannsculo/JobCatcher
Take this repo as a training for webscrapping and a try to reach something
usefull for people who think diversity in jobboard websites doesn't ease
to find opportunities.

The project is fully in development and many features need to be implemented.
It is developed in Python. This is my first time I use Python on a non-basic
project. So I guess my code is not so pythonic ... yet. Feel free to help me or
show me mistakes I could have made or improvements I could do.

## Dependencies

	python-html2text, python-requests, python-beautifulsoup, chromedriver

## Usage (mainly development options for now)

    --all              sync the blacklist, fetch the offers and generates reports.
    --feeds            download the all feeds in the config
    --feed=JOBBOARD    download only the feed from JOBBOARD in the config
    --pages            download the all pages in the config
    --page=JOBBOARD    download only the pages from JOBBOARD in the config
    --inserts          inserts all pages to offers
    --insert=JOBBOARD  insert JOBBOARD pages to offers
    --moves            move datas to offer
    --move=JOBBOARD    move JOBBOARD datas to offer
    --clean=JOBBOARD   clean offers from JOBBOARD source
    --report           generate a full report
    --version          output version information and exit

Reports are generated into the local "www" directory.

I start jobcatcher.py -s manually with crontab for now. But this should change
soon.

# List of supported Job Boards

### Partially working

In this part, some of the websites below are not full working, some information
are missing when webscrapping.

- Apec.fr (France)
- Cadreonline (France)
- PoleEmploi (France)
- RegionsJob
 - CentreJob (France)
 - NordJob (France)
 - PacaJob (France)
 - RhoneJob (France)
 - EstJob (France)
 - OuestJob (France)
 - SudOuestJob (France)
 - ParisJob (France)
- Sept lieues (France)

### TODO

- Monster
- Eures (Europe)
- Progressive Recruitment (France)
- Lolix.org (France)
- Linux.com (Int.)
- L'eXpress-Board (France)
- Remixjobs.com (France)

## Installation

### Debian, Ubuntu

    # Install a packages
    apt-get update
    apt-get install sqlite3 python-pip git
    pip install virtualenv virtualenvwrapper


    # Configure virtualenvwrapper
    cat << EOF >> ~/.bashrc
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    source /usr/local/bin/virtualenvwrapper.sh
    EOF
    source ~/.bashrc

    # Prepare jobcatcher environment
    mkvirtualenv --no-site-packages -p /usr/bin/python2.7 jobcatcher
    add2virtualenv /opt/JobCatcher

    # Install jobcatcher project
    cd opt
    git clone -b unstable https://github.com/badele/JobCatcher.git
    cd JobCatcher
    pip install -r requirements.txt

## Utilisation

Modify the config.py and execute

    workon jobcatcher
    python jobcatcher.py --all


Help us to add new job boards to JobCatcher ! :)

## Contributors

- Yoann Sculo - [www.yoannsculo.fr](http://www.yoannsculo.fr)
- Bruno Adelé - [bruno.adele.im](http://bruno.adele.im)
- Yankel Scialom - [github](https://github.com/yscialom)
- Adrien Martin [martegy.net](martegy.net)