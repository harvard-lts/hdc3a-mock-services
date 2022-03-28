# hdc3a-mock-services
Mock services for Starfish and DRS Ingest to allow DIMS and DTS to function without being connected to the actual services.

## Diagram
The diagram below outlines what the flow of control looks like using the mock services.

![DVN to DRS Mock Flow](https://github.com/harvard-lts/hdc3a-mock-services/blob/HDC114/ReadmeDocs/Dataverse-to-DRS-Mock%20Diagram.png)

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

The real Starfish makes a transfer that may succeed or fail.  We want to be able to test both.
Therefore, the Transfer Queue notifies the Mock Starfish Service whether to mock a successful or failed transfer using the following two queues:
- `STARFISH_TRANSFER_QUEUE_CONSUME_SUCCESS_NAME`
- `STARFISH_TRANSFER_QUEUE_CONSUME_FAILURE_NAME`


3. Start up the local DTS (instructions here: https://github.com/harvard-lts/drs-translation-service)

## Testing

When testing, the following .env variables will need to have the same values in order for the flow to work properly:

- hdc3a-mock-services PROCESS_QUEUE_NAME = dts-translation-service PROCESS_QUEUE_CONSUME_NAME

### Starfish
Exec into the container:

```
docker exec -it hdc3a-mock-services bash
```

#### Mocking a Success:

1. Check the enque/dequue count on the queue `STARFISH_TRANSFER_QUEUE_CONSUME_SUCCESS_NAME` (the default name if you did not change it is transfer-ready-success)

2. Type the command

```
python mqutils/notify_dvn_data_ready.py success
```

3. Check the `STARFISH_TRANSFER_QUEUE_CONSUME_SUCCESS_NAME` and verify that the pending messages incremented.  The listener will pick it up but take a few seconds (by design) to handle it.

4. Once the message is picked up, a new message should appear on the `STARFISH_TRANSFER_QUEUE_PUBLISH_NAME` (default name is dropbox-transfer-status).  If DIMS is not configured to pick up the messages from this queue, the message should remain in pending.  You can check that it has a status of success.

#### Mocking a Failure:

1. Check the enque/dequue count on the queue `STARFISH_TRANSFER_QUEUE_CONSUME_FAILURE_NAME` (the default name if you did not change it is transfer-ready-failure)

2. Type the command

```
python mqutils/notify_dvn_data_ready.py failure
```

3. Check the `STARFISH_TRANSFER_QUEUE_CONSUME_FAILURE_NAME` and verify that the pending messages incremented.  The listener will pick it up but take a few seconds (by design) to handle it.

4. Once the message is picked up, a new message should appear on the `STARFISH_TRANSFER_QUEUE_PUBLISH_NAME` (default name is dropbox-transfer-success).  If DIMS is not configured to pick up the messages from this queue, the message should remain in pending.  You can check that it has a status of failure.



### DRS Ingest

1. Check the enque/dequue count on the queue `PROCESS_QUEUE_NAME` (the default name if you did not change it is dims-data-ready)

2. Type the command

```
python mqutils/notify_dropbox_data_ready.py
```

3. Check the `PROCESS_QUEUE_NAME` and verify that the pending messages incremented.  The listener will pick it up but take a few seconds (by design) to handle it.

4. Once the message is picked up, it moves through a workflow that expects DTS to assist:

- DTS sends a message to the `DRS_QUEUE_CONSUME_NAME` to trigger the mock DRS Ingest.  
- Mock DRS Ingest sends a message to the ``DRS_TOPIC_NAME` which is picked up by DTS
- DTS sends a message to the process queue configured in DTS called `drs-ingest-status`

If DIMS is not configured to pick up the messages from `drs-ingest-status`, the message should remain in pending.  You can check that ii arrived.
