# tf-registry
Implementation of the Terraform Module Registry

# Quick Start



# Installation

## Requirements

* A database
    * PostgreSQL is recommended
* Docker


# Upgrading

Simply deploy the newer version of tf-registry. 

Since database migrations are automatically run on startup it is recommended
to upgrade one version at a time.


# API Documentation

The API has a fully documented swagger spec. Simply visit `/swagger/ui` on your registry installation.

# Development

## Requirements

* Docker and Docker Compose
* Python 3.6+
* Pipenv https://pipenv.readthedocs.io/en/latest/
* Terraform https://www.terraform.io/
* make

## Setup

1. Run `make deps` to setup the python environment
1. Run `make s3`
    * This will spin up a Minio S3 docker container to store artifacts

## Run

1. Run `make local`
    * This will launch the python application with an SQLite database
1. Navigate to `http://127.0.0.1:8080/swagger/ui`
1. Before running terraform set the `TERRAFORM_CONFIG` environment variable to `hack/.terraformrc`
    * `export TERRAFORM_CONFIG=$(pwd)/hack/.terraformrc`

## Cleanup

1. Stop the python application
1. Run `make clean`
 

# TODO

- [X] Storage
    * ~~Currently there is no way to upload/download modules~~
- [ ] Authentication and Authorization
    * Use OpenID OAuth 
- [ ] Testing and CI
    * testing all the things is very important
- [ ] Docker Image and Quick Start
    * create a docker image and quickstart for a fast local demo
- [ ] CLI
    * https://github.com/rmb938/tf-registry-cli
- [ ] Terraform Provider
    * https://github.com/rmb938/terraform-provider-tfregistry