import sys, datetime, json, logging, os, os.path
import mqutils as mqutils
import mqlistener as mqlistener
 
logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)


def notify_dvn_data_ready_for_transfer_service(doi_name):
    '''Creates a json message to be consumed by the real transfer service'''
    s3_bucket=os.getenv("S3_BUCKET_NAME", "dataverse-export-dev")
    destination_path=os.path.join("/home/appuser/local/dropbox",doi_name)
    dropbox_path=os.getenv("DROPBOX_PATH", "/home/appuser/local/dropbox")
    destination_path=os.path.join(dropbox_path,doi_name)

    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": "12345",
            "s3_path": doi_name,
            "s3_bucket_name": s3_bucket,
            "destination_path": destination_path,
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
      
def notify_dvn_data_ready_with_success_outcome():
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data is ready to process.  This is normally placed on the queue by
    the DRS Import Management Service.  It is telling the mock services that
    a success message should be returned.'''
    
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": "12345",
            "s3_path": "/path/to/data",
            "s3_bucket_name": "dataverse-export-dev",
            "destination_path": "/home/appuser/dropbox",
            "admin_metadata": {"original_queue": "myqueue", "retry_count":0}
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_success_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO {} notify_dvn_data_ready_with_success_outcome".format(connection_params.queue))
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message

def notify_dvn_data_ready_with_failure_outcome():
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data is ready to process.  This is normally placed on the queue by
    the DRS Import Management Service.  It is telling the mock services that
    a failure message should be returned.'''
    
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": "12345",
            "s3_path": "/path/to/data",
            "s3_bucket_name": "dataverse-export-dev",
            "destination_path": "/home/appuser/dropbox",
            "admin_metadata": {"original_queue": "myqueue", "retry_count":0}
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_failure_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO {} notify_dvn_data_ready_with_failure_outcome".format(connection_params.queue))
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message


if __name__ == "__main__":
    args = sys.argv[1:]
    value = "success"
    if len(args) >= 1:
        value = args[0] 
    else:
        raise RuntimeException("An argument of success, failure, or the doi id must be supplied")
     
    if (value == "success"):    
        notify_dvn_data_ready_with_success_outcome()   
    elif (value == "failure"):
        notify_dvn_data_ready_with_failure_outcome()
    else:
        notify_dvn_data_ready_for_transfer_service(value)
