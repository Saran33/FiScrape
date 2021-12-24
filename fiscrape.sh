#!/bin/sh
# get the start date and time
start_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${start_datetime} - starting fiscrape"

# go to the spider directory
export PATH=$PATH:/Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape

if [ -d "$FISCRAPE_PATH"]; then
    if [ -L "$FISCRAPE_PATH" ]; then
        echo "{$FISCRAPE_PATH}"
        cd $FISCRAPE_PATH
    elif [ ! -d "$FISCRAPE_PATH"];
    then
        cd /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape
    fi
fi

# Activate env:
# source/bin/activate/YOUR_VENV
source /Users/zenman618/opt/anaconda3/etc/profile.d/conda.sh
conda activate pwepip

# prevent click, which pipenv relies on, from freaking out to due to lack of locale info https://click.palletsprojects.com/en/7.x/python3/
export LC_ALL=en_US.utf-8

# run the spider (enter your search term. e.g. 'bitcoin'. 't' represents scraping articles published today only. The '\n' is a new line.)

previous_instance_active () {
  pgrep -f "printf 'bitcoin\nt' | python3 fiscrape.py" &>/dev/null;
}

if previous_instance_active
then 
  "Previous instance is still active at ${start_datetime}, aborting ... "
  exit
else
#   $ENV printf "bitcoin\nt" | python3 fiscrape.py
  printf "bitcoin\nt" | python3 fiscrape.py
fi

# $ENV printf "bitcoin\nt" | python3 fiscrape.py
# printf "bitcoin\nt" | python3 fiscrape.py

# get the end date and time
end_datetime=$(date '+%m_%d_%Y_%H_%M_%S')
echo "${end_datetime} - fiscrape finished successfully"