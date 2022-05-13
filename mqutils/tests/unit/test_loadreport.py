import pytest, sys, os, os.path, shutil
sys.path.append('mqutils')
import notification_manager

def test_send_loadreport():
    '''Places a load report into the dropbox'''
    notification_manager.send_drs_load_report("test_package", True, False)
    
    load_report_dest = os.getenv("LOADREPORT_PATH")
    sample_load_report = os.getenv("SAMPLE_LOADREPORT")
    path_to_lr = os.path.join(load_report_dest, "test_package", os.path.basename(sample_load_report))
    #Verify that the load report exists
    assert os.path.exists(os.path.join(path_to_lr))

    cleanup_reports(os.path.join(load_report_dest, "test_package"))

def cleanup_reports(dir_to_cleanup):
    '''Removes the report that was moved to the given dir'''
    try:
        shutil.rmtree(dir_to_cleanup)
    except OSError as e:
        print("Error: %s : %s" % (dir_to_cleanup, e.strerror))
        
def test_send_batch_failed():
    '''Places a failed batch notification into the dropbox'''
    notification_manager.send_drs_load_report("test_package", False, False)
    
    dropbox_dest = os.getenv("DROPBOX_PATH")
    path_to_batch = os.path.join(dropbox_dest, "test_package", "batch.xml.failed")
    #Verify that the failed marker exists
    assert os.path.exists(os.path.join(path_to_batch))

    cleanup_reports(os.path.join(dropbox_dest, "test_package"))
