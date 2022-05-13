import sys, datetime, json, logging, os
import mqutils as mqutils
import mqlistener as mqlistener

logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)
       
def notify_data_ready_process_message(package):
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data is ready to process.  This is normally placed on the queue by
    the DRS Import Management Service'''
    message = "No message"
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": package,
            "application_name": "Dataverse",
            "destination_path": "/path/to/object",
            "admin_metadata": {"original_queue": os.getenv('PROCESS_QUEUE_NAME'), "retry_count":0}
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_process_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO PROCDSS QUEUE notify_data_ready_process_message")
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message


if __name__ == "__main__":
    args = sys.argv[1:]
    value ="12345"
    if len(args) > 0:
        value = args[0]
    notify_data_ready_process_message(value)
