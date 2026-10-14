import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.application_tracker import ApplicationTracker

def test_application_tracker():
    tracker = ApplicationTracker()
    apps = tracker.get_applications()
    assert len(apps) >= 2
    
    # Add an app
    app_id = tracker.add_application({
        "company": "TestCorp",
        "role": "QA Engineer",
        "status": "SAVED"
    })
    
    tracker.update_application_status(app_id, "APPLIED")
    
    apps_after = tracker.get_applications()
    test_app = [a for a in apps_after if a['id'] == app_id][0]
    
    assert test_app['status'] == 'APPLIED'
