# Team 1: Recommender System
A movie recommender system for a movie streaming service with about 1 million customers and 27k movies.

## Technologies
This project is created with:
* FastAPI
* Docker Compose
* Prometheus
* Grafana
* MongoDB
* Python 

## Server Infrastructure

![Architecture](.img/server-infra.png)

## At the root of the repository

### Starting the system

``` bash
docker-compose up
```

### Stopping the system

``` bash
docker-compose down
```

## Usage 
To use the recommeder system:

1. Connect to the [McGill Computer Science VPN](https://www.cs.mcgill.ca/docs/remote/dynamic/) (e.g. ssh -D 9000 [username]@ubuntu.cs.mcgill.ca).
2. Request movie recommendations by accessing the following URL:
    
      `http://fall2020-comp598-1.cs.mcgill.ca:8082/recommend/[USER_ID]`


## Testing

## Project Structure
```
├── .github       
│   └── workflows                   <- Github Action workflows to automate testing and deployment.
├── data       
│   └── scripts                     <- Scripts to gather or generate training data.
├── model              
│   └── api                                  
│       ├── app                     <- Source code for FastAPI app which exposes the recommendation model as a service. 
│       ├── tests                   <- Unit tests for FastAPI app. 
│       ├── Dockerfile                        
│       └── requirements.txt                  
│   └── sync_script                 <- Scripts to sync data between local machine and VM (using GoogleDrive as intermediary storage).
│       ├── automated_GPU.py        <- Uploads new model from local machine to Google Drive.
│       ├── automated_VM.py         <- Downloads latest version of model from Google Drive to VM. 
│       └── client_secret.json      <- Client secrets for Google Drive. 
│   └── train                       <- Scripts to train model and perform offline evaluation.
├── telemetry 
│   ├── prometheus                  <- Config and docker-compose.yml for Prometheus server. 
│   ├── tests                       <- Unit tests for handler and parser modules.   
│   ├── __init__.py                           
│   ├── log_handlers.py             <- Collects rate and watch events from Kafka records and stores them in MongoDB.
│   ├── parser.py                   <- Helper module to parse Kafka records. 
│   └── ctr_handlers.py             <- Computes daily click-through-rate from Kafka records and stores it in MongoDB. 
├── README.md                       <- The top-level README for developers using this project.
├── docker-compose.yml              <- The top-level docker compose config. Starts the FastAPI app, the MongoDB, and the Prometheus server.
└── requirements.txt                <- The top-level requirements. All requirements for unit tests are specified here.  

```
