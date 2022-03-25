import os, json, time, datetime, stomp

class ConnectionParams:
    def __init__(self, conn, queue, host, port, user, password):
        self.conn = conn
        self.queue = queue
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        
def get_transfer_success_mq_connection():
    print("************************ MQUTILS - GET_TRANSFER_MQ_CONNECTION *******************************")
    try:
        host = os.getenv('TRANSFER_MQ_HOST')
        port = os.getenv('TRANSFER_MQ_PORT')
        user = os.getenv('TRANSFER_MQ_USER')
        password = os.getenv('TRANSFER_MQ_PASSWORD')
        queue = os.getenv('STARFISH_TRANSFER_QUEUE_CONSUME_SUCCESS_NAME')

        conn = stomp.Connection([(host, port)], heartbeats=(40000, 40000), keepalive=True)
        conn.set_ssl([(host, port)])
        connection_params = ConnectionParams(conn, queue, host, port, user, password)
        conn.connect(user, password, wait=True)
    except Exception as e:
        print(e)
        raise(e)
    return connection_params

def get_transfer_failure_mq_connection():
    print("************************ MQUTILS - GET_TRANSFER_MQ_CONNECTION *******************************")
    try:
        host = os.getenv('TRANSFER_MQ_HOST')
        port = os.getenv('TRANSFER_MQ_PORT')
        user = os.getenv('TRANSFER_MQ_USER')
        password = os.getenv('TRANSFER_MQ_PASSWORD')
        queue = os.getenv('STARFISH_TRANSFER_QUEUE_CONSUME_FAILURE_NAME')
        conn = stomp.Connection([(host, port)], heartbeats=(40000, 40000), keepalive=True)
        conn.set_ssl([(host, port)])
        connection_params = ConnectionParams(conn, queue, host, port, user, password)
        conn.connect(user, password, wait=True)
    except Exception as e:
        print(e)
        raise(e)
    return connection_params

        
def get_drs_mq_connection():
    print("************************ MQUTILS - GET_DRS_MQ_CONNECTION *******************************")
    try:
        host = os.getenv('DRS_MQ_HOST')
        port = os.getenv('DRS_MQ_PORT')
        user = os.getenv('DRS_MQ_USER')
        password = os.getenv('DRS_MQ_PASSWORD')
        queue = os.getenv('DRS_QUEUE_CONSUME_NAME')

        print("************************ QUEUE: {} *******************************".format(queue))
    
        conn = stomp.Connection([(host, port)], heartbeats=(40000, 40000), keepalive=True)
        conn.set_ssl([(host, port)])
        connection_params = ConnectionParams(conn, queue, host, port, user, password)
        conn.connect(user, password, wait=True)
    except Exception as e:
        print(e)
        raise(e)
    return connection_params

def get_process_mq_connection():
    print("************************ MQUTILS - GET_PROCESS_MQ_CONNECTION *******************************")
    try:
        host = os.getenv('PROCESS_MQ_HOST')
        port = os.getenv('PROCESS_MQ_PORT')
        user = os.getenv('PROCESS_MQ_USER')
        password = os.getenv('PROCESS_MQ_PASSWORD')
        queue = os.getenv('PROCESS_QUEUE_NAME')

        conn = stomp.Connection([(host, port)], heartbeats=(40000, 40000), keepalive=True)
        conn.set_ssl([(host, port)])
        connection_params = ConnectionParams(conn, queue, host, port, user, password)
        conn.connect(user, password, wait=True)
    except Exception as e:
        print(e)
        raise(e)
    return connection_params
