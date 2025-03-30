from datetime import datetime, timedelta
from backend.baby_manager import BabyManager

def test_feeding_logic():
    mgr = BabyManager()
    base_time = datetime(2025, 3, 30, 12, 0)
    
    # Initial state - no feedings
    assert mgr.should_feed(current_time=base_time) is True
    
    # Record 150ml feeding
    mgr.record_feeding(150, base_time)
    assert mgr.should_feed(current_time=base_time) is False  # Under 3 hours
    
    # Test 3 hour threshold
    mgr.record_feeding(150, base_time)
    three_hours_later = base_time + timedelta(hours=3, minutes=1)
    assert mgr.should_feed(current_time=three_hours_later) is True
    
    # Test 100ml boundary
    mgr.record_feeding(99, base_time)
    two_hours_later = base_time + timedelta(hours=2, minutes=1)
    assert mgr.should_feed(current_time=two_hours_later) is True
    
    # Test 100ml with insufficient time
    mgr.record_feeding(100, base_time)
    assert mgr.should_feed(current_time=base_time) is False

def test_sleep_logic():
    mgr = BabyManager()
    base_time = datetime(2025, 3, 30, 12, 0)
    
    # No sleep recorded
    assert mgr.should_sleep(current_time=base_time) is True
    
    # Record sleep ending now
    mgr.record_sleep(base_time - timedelta(hours=1), base_time)
    assert mgr.should_sleep(current_time=base_time) is False
    
    # 2 hours awake
    two_hours_ago = base_time - timedelta(hours=2, minutes=1)
    test_time = base_time + timedelta(hours=2, minutes=1)
    mgr.record_sleep(base_time - timedelta(hours=1), base_time)
    assert mgr.should_sleep(current_time=test_time) is True

def test_diaper_logic():
    mgr = BabyManager()
    base_time = datetime(2025, 3, 30, 12, 0)
    
    # No changes
    assert mgr.should_change_diaper(current_time=base_time) is True
    
    # Recent change
    mgr.record_diaper_change(base_time)
    assert mgr.should_change_diaper(current_time=base_time) is False
    
    # Over 2 hours
    test_time = base_time + timedelta(hours=2, minutes=1)
    mgr.record_diaper_change(base_time)
    assert mgr.should_change_diaper(current_time=test_time) is True
