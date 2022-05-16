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
        #Helps toggle between failure and success
        self.issuccessmock = True
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
        logging.debug('DRS Ingest complete.  Sending success message.')
        #Place a load report into the dropbox
        notification_manager.send_drs_load_report(self.message_data["package_id"], self.issuccessmock)
        self.issuccessmock = not self.issuccessmock
        
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

def get_drsbatchreadymqlistener():
    connection_params = mqutils.get_drs_mq_connection()
    mqlistener = MqListener(connection_params)
    return mqlistener
    
if __name__ == "__main__":
    initialize_drsbatchreadylistener()   
