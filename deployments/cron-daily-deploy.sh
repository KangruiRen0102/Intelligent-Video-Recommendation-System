### This file must be executed from the root directory of this project repository ###

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
        container=$(docker ps --format "{{.ID}} {{.Image}} {{.Ports}}" | awk '(index($4, ${port}) != 0) {print $1}')
        docker rm -f ${container}
        sleep 1h
    done
}


# Save pid in case of rollback this process must be killed
echo $BASHPID > "${dir}/cdd-pid"

# Get filepath of the deployment archive
file="deployments.csv"
dir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
filepath="${dir}/${file}"

# Add snapshot of upcoming deployment to document
date=$(date --rfc-3339="second")
commit=$(git log | head -n 1 | cut -d " " -f 2)
if [ $(tail -n 1 ${filepath} | sed '1d' | wc -l) -eq 0 ]
then
    version=1
else
    version=$(($(tail -n 1 ${filepath} | cut -d "," -f 3) + 1))
fi
echo "${date},${commit},${version},false"  >> "${filepath}"

# Build image for the new deployment
repo="prod_fastapi_server"
docker build -t ${repo}:${version} -f model/api/Dockerfile .

# Deploy 3 containers with the new image, 1 hour delay between
deploy 7003 7005

# Remove 3 containers with the old image, 1 hour delay between
remove 7000  7002

# Deploy 3 containers with the new image, 1 hour delay between
deploy 7000  7002

# Remove 3 containers with the new image, 1 hour delay between
remove 7003 7005 
