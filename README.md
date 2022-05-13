# hdc3a-mock-services
Mock services for Starfish and DRS Ingest to allow DIMS and DTS to function without being connected to the actual services.

## Diagram
The diagram below outlines what the flow of control looks like using the mock services.

![DVN to DRS Mock Flow](ReadmeDocs/Dataverse-to-DRS-Mock%20Diagram.png)

## Local setup
    
1. Make a copy of the env-template.txt to .env and modify the user and password variables.

2. Start the container
    
```
docker-compose -f docker-compose-local.yml up -d --build --force-recreate
```

This will set up listeners to the following 3 queues listed in the .env:

The real DRS Ingest monitors dropboxes where the mock DRS Ingest service does not.
Therefore, the `DRS_QUEUE_CONSUME_NAME` notifies the Mock DRS Ingest Service that it 'received and ingested' a batch so that it can notify the drs updated topic

- `DRS_QUEUE_CONSUME_NAME`



3. Start up the local DTS (instructions here: https://github.com/harvard-lts/drs-translation-service)

## Testing

When testing, the following .env variables will need to have the same values in order for the flow to work properly:

- hdc3a-mock-services PROCESS_QUEUE_NAME = drs-translation-service PROCESS_QUEUE_CONSUME_NAME

If using DIMS:

- drs-translation-sesrvice PROCESS_QUEUE_CONSUME_NAME = drs-import-management-service MQ_PROCESS_QUEUE_PROCESS_READY

#### Triggering the real Transfer Service WITHOUT DIMS:

1. Exec into the container:

```
docker exec -it hdc3a-mock-services bash
```

2. Type the command and supply the full DOI that is in S3

```
python mqutils/notify_dvn_data_ready.py <DOI name>
```

### DRS Ingest

1. Exec into the container:

```
docker exec -it hdc3a-mock-services bash
```

2. Check the enque/dequue count on the queue `PROCESS_QUEUE_NAME` (the default name if you did not change it is dims-data-ready)

3. Type the command

```
python mqutils/notify_dropbox_data_ready.py <DOI name (optional>
```

4. Once the message is picked up, it moves through a workflow that expects DTS to assist:

- DTS sends a message to the `DRS_QUEUE_CONSUME_NAME` to trigger the mock DRS Ingest.  
- Mock DRS Ingest places a load report or batch.xml.failed into the dropbox which is picked up by DTS
- DTS sends a message to the process queue configured in DTS called `drs-ingest-status`

If DIMS is not configured to pick up the messages from `drs-ingest-status`, the message should remain in pending.  You can check that ii arrived.
