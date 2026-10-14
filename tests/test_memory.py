import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from memory.profile_memory import ProfileMemory

def test_profile_memory():
    db = ProfileMemory()
    profile = db.get_profile()
    assert isinstance(profile, dict)
    assert 'name' in profile
    assert profile['name'] == 'Jane Doe'
