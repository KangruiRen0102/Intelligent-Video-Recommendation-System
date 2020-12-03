### This file should be run from the root of this code repository ###


# Creating deployment log file
dir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
FILE=${dir}/deployments/deployments.csv
if [ ! -f $FILE ]
then
    echo "date,commit,version,rollback" >> $FILE
fi

# Starting stable components of our infrastructure
docker-compose down
docker-compose up -d
