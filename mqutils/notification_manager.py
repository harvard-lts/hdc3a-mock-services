import sys, os, logging, stomp, time, datetime, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import mqutils as mqutils
import mqlistener as mqlistener
from mqexception import MQException

logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)
    
def notify_starfish_transfer_success_message():
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data was successfully transferred.  This is normally placed on the queue by
    Starfish'''
    message = "No message"
    try:
        timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()
       
        #Add more details that will be needed from the load report.
        msg_json = {
            "transfer_status": "success",
            "destination_path": "/path/to/object"
        }

        logging.debug("********SENDING SAMPLE MESSAGE TO TRANSFER QUEUE*******")
        logging.debug(msg_json)
        logging.debug("**********************************")
        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_success_mq_connection()
        connection_params.conn.send(os.getenv('STARFISH_TRANSFER_QUEUE_PUBLISH_NAME'), message, headers = {"persistent": "true"})
    except Exception as e:
        print(e)
        raise(e)
    return message

def notify_starfish_transfer_failure_message():
    '''Creates a dummy queue json message to notify the queue that the 
    DVN data failed the transfer.  This is normally placed on the queue by
    Starfish'''
    message = "No message"
    try:
        timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()
       
        #Add more details that will be needed from the load report.
        msg_json = {
            "transfer_status": "failure",
            "destination_path": "/path/to/object"
        }

        logging.debug("********SENDING SAMPLE MESSAGE TO TRANSFER QUEUE*******")
        logging.debug(msg_json)
        logging.debug("**********************************")
        message = json.dumps(msg_json)
        connection_params = mqutils.get_transfer_failure_mq_connection()
        connection_params.conn.send(os.getenv('STARFISH_TRANSFER_QUEUE_PUBLISH_NAME'), message, headers = {"persistent": "true"})
    except Exception as e:
        print(e)
        raise(e)
    return message

def notify_drs_ingest_success_message():
    '''Creates a dummy queue drs json message This is normally placed on the topic by
    the DRS Ingest'''
    message = "No message"
    try:
        timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat()
       
        #Sample DRS Ingest message.
        msg_json = {"data":
                    {"objectId":123,
                     "contentModel":"CMID-5.0",
                     "accessFlag":"N",
                     "isFile":"false",
                     "ocflObjectKey":"12345678",
                     "ocflObjectPath":"/8765/4321/12345678",
                     "primaryUrn":"URN-3.HUL.ARCH:123456",
                     "status":"current"}
                    }

        logging.debug("********SENDING DRS INGEST MESSAGE TO DRS TOPIC*******")
        logging.debug(msg_json)
        logging.debug("**********************************")
        message = json.dumps(msg_json)
        message = json.dumps(msg_json)
        connection_params = mqutils.get_drs_mq_connection()
        connection_params.conn.send(os.getenv('DRS_TOPIC_NAME'), message, headers = {"persistent": "true"})
    except Exception as e:
        print(e)
        raise(e)
    return message

