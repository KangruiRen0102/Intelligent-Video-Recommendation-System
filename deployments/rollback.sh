### This file is triggered by another process whenever the deployment has been unsuccessful ### 

deploy() {
    for port in $(seq $1 $2)
    do
        docker run -d -p ${port}:80 ${repo}:${version}
        sleep 1h
    done
}

remove() {
    for port in $(seq $1 $2)
    do
        container=$(docker ps --format "{{.ID}} {{.Image}} {{.Ports}}" | awk -vport="$port" '(index($3, port) != 0) {print $1}')
        docker rm -f ${container}
        sleep 1h
    done
}


# Find and stop the deployment process
dir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cdd_filepath="${dir}/cdd-pid"
read -r cddpid < $cdd_filepath
kill -9 $cddpid

# Mark the last deployment as unsuccesful
line=$(wc -l "${dir}/deployments.csv" | cut -d " " -f 1)
sed -i -e "${line}s/false/true/" "${dir}/deployments.csv"

# Find the last working version
repo="prod_fastapi_server"
version=$(grep "false" "${dir}/deployments.csv" | tail -n 1 | cut -d "," -f 3)

# Swap containers for a previous working version
for port in {7000..7002}
do
    remove $port $port
    deploy $port $port
done

# Remove possibly existing containers, to eliminate cases of transient states
remove 7003 7005
