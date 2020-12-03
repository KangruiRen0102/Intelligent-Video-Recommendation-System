### This file should be run from the root of this code repository ###
docker-compose up -d
echo "date,commit,version,rollback\n" > deployments/deployments.csv
#bash deployments/cron-daily-deploy.sh
