.PHONY: develop s3 clean local

deps:  ## Setup the python environment
	pipenv install

s3:  ## launch the minio s3 container
	docker-compose -p tf_registry_s3 -f hack/docker-compose.yaml up

clean:  ## clean up the local environment
	rm -rf hack/registry.db
	docker-compose -p tf_registry_s3 -f hack/docker-compose.yaml down -v

local:  ## Run the python application
	pipenv run registry --db-url sqlite:///hack/registry.db --s3-endpoint http://127.0.0.1:9000 --s3-access-key-id Z4DCGH3MOP1N1GVO9146 --s3-secret-access-key EB5gj1VgmfmRGfnSfcM06ZPG5ah9FB9DsUEISRi0 --s3-bucket local

help:  ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort