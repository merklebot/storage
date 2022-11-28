# Storage

Multy-tenant RESTful HTTP API server for encrypted data storing and retrieval in IPFS and web3 storages with per-user workload accounting.

## Launch

### Run locally for development

Assuming we are in the repository root directory.

1. Set `.env` variables

    ```bash
    ...
    IPFS_HTTP_PROVIDER=http://localhost:5001
    POSTGRES_SERVER=localhost
    ```

1. Run local database and IPFS node

    ```console
    docker compose up db kubo
    ```

1. Launch service instance

    ```console
    ./start.sh
    ```

1. Create a tenant and an API key

    ```console
    $ python -m storage --tenant-create dev && python -m storage --create-api-key-for-tenant dev
    2022-11-28 17:47:08.555 | INFO     | __main__:<module>:75 - tenant created, tenant.name='dev', tenant.schema='dev', tenant.host='dev'
    0dOzYgisKiKBJFM5Y60J7p96U48IdmsuV_GOan0c15fTNQuxee6sPSgMMNGDDeCwtKK6BzScI7ORJ9dqfQOThw
    ```

### Deploy to cluster

Assuming we are in the repository root directory and cluster leader Docker context is available locally by `merklebot` name.

1. Set `.env` variables

    ```bash
    ...
    IPFS_HTTP_PROVIDER=http://kubo_kubo:5001
    POSTGRES_SERVER=storage_db
    ```

1. Connect to swam leader

    ```console
    docker context use merklebot
    ```

1. Remove an old version

    ```console
    docker stack rm storage
    ```

1. Run a new version

    ```consol
    docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml storage
    ```

1. Check services are ok (at least 1 replica is running)

    ```console
    $ docker service ls
    ID             NAME              MODE         REPLICAS   IMAGE                            PORTS
    6zw0odgoqjuf   storage_db        replicated   1/1        postgres:15
    met55xby5gmf   storage_storage   replicated   1/1        ghcr.io/merklebot/storage:main
    ```
