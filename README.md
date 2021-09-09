
# I2b2-cdi-qs
I2b2-cdi-qs provides a command line interface to import, delete concepts and facts and encounters.

## I2B2-ETL
You can pull and run i2b2/i2b2-etl docker image with the help of `docker-compose-i2b2-etl.yml` file. Please follow the below steps:
1. Set the required environment variable inside `docker-compose-i2b2-etl.yml` file
    ```.env
    I2B2_DS_CRC_IP=i2b2-mssql
    I2B2_DS_CRC_USER=
    I2B2_DS_CRC_PASS=
    I2B2_DS_CRC_PORT=1433
    I2B2_DS_CRC_DB=i2b2demodata

    I2B2_DS_ONT_IP=i2b2-mssql
    I2B2_DS_ONT_USER=
    I2B2_DS_ONT_PASS=
    I2B2_DS_ONT_PORT=1433
    I2B2_DS_ONT_DB=i2b2metadata

    CSV_DELIMITER=,
    MAX_VALIDATION_ERROR_COUNT=10000
    ```
2. Start I2B2-ETL
    ```shell
    ./start-i2b2-etl.sh
    ```
> **_NOTE:_** After starting etl, it will create ```data``` directory whetre you can put all the data files inside that directory and refer those files while import.

## Executing the I2B2-ETL 
### I2B2-ETL commands
Below commands helps to play with I2B2-ETL

### Help
This will list all possible operation of i2b2-etl
```shell
$ etl --help
OR
$ etl -h
```

### Starting the i2b2 and cdi docker containers
```shell
$ etl --start-i2b2

$ etl --start-cdi
```

### Delete all data
This is high level command to delete all data from i2b2.
```shell
$ etl --delete-data
OR
$ etl -dd
```

### Load data
This is high level command to load data into i2b2. Provide the `<folder-name>` where files exists.
```shell
$ etl --load-data <folder-name>
OR
$ etl -ld <folder-name>
```
> **_NOTE:_** File names should be strictly followed. For concepts - ['concepts.csv', 'derived_concepts.csv','concept_mappings.csv'] and for data - ['mrn.csv', 'patients.csv', 'encounters.csv', 'facts.csv']

### Delete concepts
```shell
$ etl --delete-concepts
OR
$ etl -dc
```

### Import concepts
```shell
$ etl -ic <one-or-more-input-files> 
OR
$ etl --import-concepts <one-or-more-input-files>
```
> **_EXAMPLE:_** $ etl -ic concepts.csv derived_concepts.csv concept_mappings.csv (Note : order does not matter)


### Delete patient mapping
```shell
$ etl -dpm
OR
$ etl --delete-patient-mappings
```

### Import patient mapping
```shell
$ etl -ipm <mrn-file> 
OR
$ etl --import-patient-mappings <mrn-file>
```

### Delete patients
```shell
$ etl -dp
OR
$ etl --delete-patients
```

### Import patients
```shell
$ etl -ip <patient-file> 
OR
$ etl --import-patients <patient-file>
```

### Delete encounter mapping
```shell
$ etl -dem
OR
$ etl --delete-encounter-mappings
```

### Delete encounters
```shell
$ etl -de
OR
$ etl --delete-encounters
```

### Import encounters
```shell
$ etl -ie <encounter-file>
OR
$ etl --import-encounters <encounter-file>
```

### Delete facts
```shell
$ etl --delete-facts
OR
$ etl -df
```

### Import facts
```shell
$ etl --import-facts <fact-file>
OR
$ etl -if <fact-file>
```

> **_NOTE:_** As patients, encounters and facts are dependent on each other, Try patient import followed by encounter and facts. 

## Separate Docker Containers 
When we would have separate docker container, following commands would be useful for executing operations on the pipeline

### Delete concepts
```shell
$ python -m i2b2_cdi.concept.perform_concept --delete-concepts
OR
$ python -m i2b2_cdi.concept.perform_concept -dc
```

### Delete facts
```shell
$ python -m i2b2_cdi.fact.perform_fact --delete-facts
OR
$ python -m i2b2_cdi.fact.perform_fact -df
```

### Import facts
```shell
$ python -m i2b2_cdi.fact.perform_fact --import-facts <fact-input-file> <mrn-input-file> <encounter-input-file>
Or
$ python -m i2b2_cdi.fact.perform_fact -if <fact-input-file> <mrn-input-file> <encounter-input-file>
```

## Dockerizing

We can build the docker image for the pipeline. Before that we must ensure the following pre-requisites on the host machine.
* `Docker version 19.03.8 and above`
* `Docker-compose version 1.25.4 and above`

> **_NOTE:_**  For building the docker image the context directory will be the root directory i.e. `i2b2-cdi-qs`

### Update .env file (when building the docker image)
You will need to update .env file available at two locations with same changes.
Update the .env file for i2b2 crc and ont parameters. Below are the locations of .env file

1. `/i2b2-cdi-qs/.env`
2. `/i2b2-cdi-qs/i2b2_cdi/resources/.env`

Use below variables to do so.

```.env
I2B2_DS_CRC_IP=i2b2-mssql
I2B2_DS_CRC_USER=
I2B2_DS_CRC_PASS=
I2B2_DS_CRC_PORT=1433
I2B2_DS_CRC_DB=i2b2demodata

I2B2_DS_ONT_IP=i2b2-mssql
I2B2_DS_ONT_USER=
I2B2_DS_ONT_PASS=
I2B2_DS_ONT_PORT=1433
I2B2_DS_ONT_DB=i2b2metadata

CSV_DELIMITER=,
MAX_VALIDATION_ERROR_COUNT=10000
```

### Let's build the docker image for the i2b2_cdi_loader module

```shell
$ export DOCKER_BUILDKIT=1

$ docker build -f i2b2_cdi/resources/docker/Dockerfile.loader --no-cache -t i2b2/i2b2-etl:<tag> .

$ docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock  --net i2b2-net i2b2/i2b2-etl:<tag> bash


## Sphinx Documentations
Source code documentations have been implemented with Sphinx. Following are the steps for creating docs.

### Install Sphinx
```shell
$ pip install -U Sphinx
```

> **_NOTE:_**  Current working directory will be  `i2b2-cdi-qs/docs/`

### Sphinx Initialization
If there are no docs created yet, below command can be used for sphinx docs initialization.
```shell
$ sphinx-quickstart
```

### Creating docs for new source code
After running below commands, you can launch index.html file from docs/html directory  
```shell
$ sphinx-apidoc -f -o source/ ../

$ make html

$ cp -r build/html/* html/
```

### Deployment to Apache2 Server
If you have apache2 server installed, you can deploy html docs to the server
```shell
$ sudo mkdir /var/www/html/i2b2-cdi

$ sudo cp -r build/html/* /var/www/html/i2b2-cdi/
```
