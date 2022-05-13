import sys, os, logging, stomp, time, datetime, json, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import mqutils as mqutils
import mqlistener as mqlistener
from mqexception import MQException

logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)
    

def send_drs_load_report(doi_name, issuccessmock, sendnotification=True):
    '''Places a load report in the dropbox.  Toggles between success and failure'''
    
    if issuccessmock:
        #Place a load report into the load report dropbox
        loadreportdest = os.getenv("LOADREPORT_PATH")
        sampleloadreport = os.getenv("SAMPLE_LOADREPORT")
        loadreportdest = os.path.join(loadreportdest, doi_name, os.path.basename(sampleloadreport))
        os.makedirs(os.path.dirname(loadreportdest), exist_ok=True)
        shutil.copyfile(sampleloadreport, loadreportdest)
        if sendnotification:
            notify_drs_ingest_complete_message(doi_name, "success") 
    else:
        #Place a batch.xml.failed in the batch
        batchfailedfile = os.getenv("DROPBOX_PATH")
        batchfailedfile = os.path.join(batchfailedfile, doi_name, "batch.xml.failed")
        os.makedirs(os.path.dirname(batchfailedfile), exist_ok=True)
        open(batchfailedfile, 'w').close()
        if sendnotification:
            notify_drs_ingest_complete_message(doi_name, "failure")    
    
def notify_drs_ingest_complete_message(package_id, status):
    try:
        msg_json = {
            "package_id": package_id,
            "application_name": "Dataverse",
            "batch_ingest_status": status
            
        }

        message = json.dumps(msg_json)
        connection_params = mqutils.get_drs_mq_connection(os.getenv("DRS_QUEUE_PUBLISH_NAME"))
        connection_params.conn.send(connection_params.queue, message, headers = {"persistent": "true"})
        logging.debug("MESSAGE TO DRS QUEUE notify_drs_ingest_complete_message")
        logging.debug(message)
    except Exception as e:
        print(e)
        raise(e)
    return message    

