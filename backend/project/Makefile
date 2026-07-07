DC = docker-compose
STORAGES_FILE = docker-compose/storages.yaml
DB_CONTAINER = example-db
LOGS = docker logs
EXEC = docker exec -it

.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} up -d


.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGES_FILE} down

.PHONY: postgres
postgres:
	${EXEC} ${DB_CONTAINER} psql

.PHONY: storages-logs
storages-logs:
	${LOGS} ${DB_CONTAINER} -f