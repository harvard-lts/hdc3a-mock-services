import sys, datetime, json, logging
import mqutils as mqutils
import mqlistener as mqlistener
 
logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)
      
def notify_dvn_data_ready_with_success_outcome():
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data is ready to process.  This is normally placed on the queue by
    the DRS Import Management Service.  It is telling the mock services that
    a success message should be returned.'''
    message = "No message"
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": "12345",
            "s3_path": "/some/path/in/s3",
            "s3_bucket_name": "my-bucket-name",
            "desination_path": "/path/to/object",
            "message": "Message"
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_success_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO PROCDSS QUEUE notify_dvn_data_ready_with_failure_outcome")
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
    message = "No message"
    try:
        #Add more details that will be needed from the load report.
        msg_json = {
            "package_id": "12345",
            "s3_path": "/some/path/in/s3",
            "s3_bucket_name": "my-bucket-name",
            "desination_path": "/path/to/object",
            "message": "Message"
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_failure_mq_connection()
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO PROCDSS QUEUE notify_dvn_data_ready_with_failure_outcome")
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message


if __name__ == "__main__":
    permitted_values = {"success", "failure"}
    args = sys.argv[1:]
    value = "success"
    if len(args) >= 1:
        value = args[0]
     
    if (value not in permitted_values):
        raise RuntimeException("Argument syntax requires either success or failure for parameters")
     
    if (value == "success"):    
        notify_dvn_data_ready_with_success_outcome()   
    else:
        notify_dvn_data_ready_with_failure_outcome()
