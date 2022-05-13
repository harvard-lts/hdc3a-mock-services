import sys, datetime, json, logging, os, os.path
import mqutils as mqutils
import mqlistener as mqlistener
 
logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)


def notify_dvn_data_ready_for_transfer_service(doi_name):
    '''Creates a json message to be consumed by the real transfer service'''
    s3_bucket=os.getenv("S3_BUCKET_NAME", "dataverse-export-dev")
    dropbox_path=os.getenv("DROPBOX_PATH", "/home/appuser/local/dropbox")
    dest_path = os.path.join(dropbox_path, doi_name)
    
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": doi_name,
            "s3_path": doi_name,
            "s3_bucket_name": s3_bucket,
            "destination_path": dest_path,
            "admin_metadata": {"original_queue": os.getenv('TRANSFER_QUEUE_CONSUME_NAME'), "retry_count":0}
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO {} notify_dvn_data_ready_for_transfer_service".format(connection_params.queue))
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0:
        raise RuntimeException("Argument syntax requires a name of the package to be transferred")
     
    value = args[0]
    notify_dvn_data_ready_for_transfer_service(value)
