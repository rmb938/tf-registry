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

Since database migrations are automatically ran on startup it is recommenced
to upgrade one version at a time.


# API Documentation

The API has a fully documented swagger spec. Simply visit `/swagger/ui` on your registry installation.

# TODO

- [ ] Authentication and Authorization
    * Use OpenID OAuth 