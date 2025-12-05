#!/usr/bin/env python3
"""
Test script for Live Ping Monitor functionality
"""

import time
from tools.live_ping_monitor import LivePingMonitor

def test_monitor_basic():
    """Test basic monitor functionality"""
    print("Testing Live Ping Monitor...")
    print("=" * 60)
    
    # Create monitor
    monitor = LivePingMonitor()
    
    # Add hosts
    print("\n1. Adding hosts...")
    hosts = ["127.0.0.1", "8.8.8.8", "google.com"]
    
    for host in hosts:
        ip = monitor.add_host(host)
        if ip:
            print(f"   ✓ Added: {host} (resolved to {ip})")
        else:
            print(f"   ✗ Failed to add: {host}")
    
    print(f"\n2. Starting monitoring...")
    monitor.start_monitoring()
    print("   ✓ Monitoring started (pinging every 1 second)")
    
    # Let it run for a few seconds
    print("\n3. Collecting data for 5 seconds...")
    for i in range(5):
        time.sleep(1)
        print(f"   ... {i+1} seconds elapsed")
    
    # Check data
    print("\n4. Checking collected data...")
    all_hosts = monitor.get_all_hosts_data()
    
    for ip, host_data in all_hosts.items():
        print(f"\n   Host: {ip}")
        if host_data.hostname:
            print(f"   Hostname: {host_data.hostname}")
        print(f"   Status: {host_data.get_status_text()}")
        print(f"   Average Latency: {host_data.get_average_latency():.1f} ms")
        print(f"   Packet Loss: {host_data.get_packet_loss():.1f}%")
        print(f"   Total Pings: {host_data.get_total_pings()}")
        
        recent = host_data.get_recent_pings()
        print(f"   Recent pings: {len(recent)} data points")
    
    # Test pause/resume
    print("\n5. Testing pause/resume...")
    monitor.pause_monitoring()
    print("   ✓ Paused")
    time.sleep(2)
    monitor.resume_monitoring()
    print("   ✓ Resumed")
    time.sleep(2)
    
    # Stop monitoring
    print("\n6. Stopping monitoring...")
    monitor.stop_monitoring()
    print("   ✓ Monitoring stopped")
    
    # Test export
    print("\n7. Testing export...")
    export_data = monitor.export_data()
    print(f"   ✓ Export data generated ({len(export_data)} characters)")
    print("\n" + "=" * 60)
    print("Preview of export data:")
    print("-" * 60)
    print(export_data[:500] + "...")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")

if __name__ == "__main__":
    try:
        test_monitor_basic()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
