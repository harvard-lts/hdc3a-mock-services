import datetime, json, os, time, traceback, stomp, sys, logging
import mqutils
import mqexception
import notification_manager

# Subscription id is unique to the subscription in this case there is only one subscription per connection
_sub_id = 1
_reconnect_attempts = 0
_max_attempts = 1000

logging.basicConfig(filename='/home/appuser/logs/mock_services.log', level=logging.DEBUG)

def subscribe_to_listener(connection_params):
    print("************************ MQUTILS MQLISTENER - CONNECT_AND_SUBSCRIBE *******************************")
    global _reconnect_attempts
    _reconnect_attempts = _reconnect_attempts + 1
    if _reconnect_attempts <= _max_attempts:
        # TODO: Retry timer with exponential backoff
        time.sleep(1)
        try:
            if not connection_params.conn.is_connected():
                connection_params.conn.connect(connection_params.user, connection_params.password, wait=True)
                print(f'subscribe_to_listener connecting {connection_params.queue} to with connection id 1 reconnect attempts: {_reconnect_attempts}', flush=True)
            else:
                print(f'connect_and_subscibe already connected {connection_params.queue} to with connection id 1 reconnect attempts {_reconnect_attempts}', flush=True)
        except Exception as e:
            logging.error('Exception on disconnect. reconnecting...')
            logging.error(traceback.format_exc())
            subscribe_to_listener(connection_params)
        else:
            connection_params.conn.subscribe(destination=connection_params.queue, id=1, ack='client-individual')
            _reconnect_attempts = 0
    else:
        logging.error('Maximum reconnect attempts reached for this connection. reconnect attempts: {}'.format(_reconnect_attempts))


class MqListener(stomp.ConnectionListener):
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.message_data = None
        self.message_id = None
        logging.debug('MqListener init')

    def on_error(self, frame):
        logging.debug('received an error "%s"' % frame.body)

    def on_message(self, frame):
        logging.debug("************************ MQLISTENER - ON_MESSAGE *******************************")
        headers, body = frame.headers, frame.body
        logging.debug('received a message headers "%s"' % headers)
        logging.debug('message body "%s"' % body)

        self.message_id = headers.get('message-id')
        try: 
            self.message_data = json.loads(body)
        except json.decoder.JSONDecodeError: 
            raise mqexception.MQException("Incorrect formatting of message detected.  Required JSON but received {} ".format(body))
        
        time.sleep(10)
        #For testing, we have separate queues to indicate whether to trigger success or failure of transfer
        if self.connection_params.queue == os.getenv('STARFISH_TRANSFER_QUEUE_CONSUME_SUCCESS_NAME'):
            logging.debug('Transfer to dropbox complete.  Sending success message.')
            #Send successful transfer message
            notification_manager.notify_starfish_transfer_success_message()
        if self.connection_params.queue == os.getenv('STARFISH_TRANSFER_QUEUE_CONSUME_FAILURE_NAME'):
            logging.debug('Transfer to dropbox failed.  Sending failed message.')
            #Send successful transfer message
            notification_manager.notify_starfish_transfer_failure_message()
        elif self.connection_params.queue == os.getenv('DRS_QUEUE_CONSUME_NAME'):
            logging.debug('DRS Ingest complete.  Sending success message.')
            #Place a load report into the dropbox
            notification_manager.send_drs_load_report()
        
        self.connection_params.conn.ack(self.message_id, 1)

        #TODO- Handle
        logging.debug(' message_data {}'.format(self.message_data))
        logging.debug(' message_id {}'.format(self.message_id))

    def on_disconnected(self):
        logging.debug('disconnected! reconnecting...')
        subscribe_to_listener(self.connection_params)
        
    def get_connection(self):
        return self.connection_params.conn
    
    def get_message_data(self):
        return self.message_data
    
    def get_message_id(self):
        return self.message_id

         
def initialize_starfishtransfersuccesslistener():
    mqlistener = get_transfersuccessmqlistener()
    conn = mqlistener.get_connection()
    conn.set_listener('', mqlistener)
    subscribe_to_listener(mqlistener.connection_params)
    # http_clients://github.com/jasonrbriggs/stomp.py/issues/206
    while True:
        time.sleep(2)
        if not conn.is_connected():
            logging.debug('Disconnected in loop, reconnecting')
            subscribe_to_listener(mqlistener.connection_params)

def initialize_starfishtransferfailurelistener():
    mqlistener = get_transferfailuremqlistener()
    conn = mqlistener.get_connection()
    conn.set_listener('', mqlistener)
    subscribe_to_listener(mqlistener.connection_params)
    # http_clients://github.com/jasonrbriggs/stomp.py/issues/206
    while True:
        time.sleep(2)
        if not conn.is_connected():
            logging.debug('Disconnected in loop, reconnecting')
            subscribe_to_listener(mqlistener.connection_params)
            
def initialize_drsbatchreadylistener():
    mqlistener = get_drsbatchreadymqlistener()
    conn = mqlistener.get_connection()
    conn.set_listener('', mqlistener)
    subscribe_to_listener(mqlistener.connection_params)
    # http_clients://github.com/jasonrbriggs/stomp.py/issues/206
    while True:
        time.sleep(2)
        if not conn.is_connected():
            logging.debug('Disconnected in loop, reconnecting')
            subscribe_to_listener(mqlistener.connection_params)
            
def get_transfersuccessmqlistener():
    '''This connection tells the mock starfish service to return
    a successful transfer message'''
    connection_params = mqutils.get_transfer_success_mq_connection()
    mqlistener = MqListener(connection_params)
    return mqlistener

def get_transferfailuremqlistener():
    '''This connection tells the mock starfish service to return
    a failed transfer message'''
    connection_params = mqutils.get_transfer_failure_mq_connection()
    mqlistener = MqListener(connection_params)
    return mqlistener

def get_drsbatchreadymqlistener():
    connection_params = mqutils.get_drs_mq_connection()
    mqlistener = MqListener(connection_params)
    return mqlistener
    
if __name__ == "__main__":
    permitted_values = {"drs", "transfersuccess", "transferfailure"}
    args = sys.argv[1:]
    listener = "drs"
    if len(args) >= 1:
        listener = args[0]
     
    if (listener not in permitted_values):
        raise RuntimeException("Argument syntax requires either drs or process for parameters")
     
    if (listener == "drs"):    
        initialize_drsbatchreadylistener()   
    elif (listener == "transfersuccess"):
        initialize_starfishtransfersuccesslistener()
    else:
        initialize_starfishtransferfailurelistener()
