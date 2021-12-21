# use 'EDITOR=nano crontab -e' to add this line to crontab, to run crawl.sh on the hour every hour
# 0 * * * * export SPIDER_PATH=/Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape && ./fiscrape.sh >> cron_log.txt 2 >& 1
HOME= /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape

*/1 * * * * (cd /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape && echo "this is a test" > /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape/testlog.txt)

*/1 * * * * (cd /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape && /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape/fiscrape.sh >> /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape/zlog.txt 2 >& 1)
# OR:
*/1 * * * * (cd /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape && export SPIDER_PATH=/Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape && /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape/fiscrape.sh >> /Volumes/X\ Files/git_packages/VisualStudioGit/FiScrape/zlog.txt 2 >& 1)


