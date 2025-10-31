#!/usr/bin/env python3

"""
Debug script to test the main application initialization.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_app_initialization():
    """Test initializing the main app to see where it fails."""
    try:
        print("🔍 Testing app initialization...")
        
        # Test imports
        print("1. Testing imports...")
        from traffic_sim.core.testapp import TrafficApp
        print("   ✅ Imports successful")
        
        # Test configuration
        print("2. Testing configuration...")
        from traffic_sim.configuration import Config
        config = Config()
        print(f"   ✅ Configuration loaded (WIDTH: {config.WIDTH}, HEIGHT: {config.HEIGHT})")
        
        # Test pygame initialization
        print("3. Testing pygame...")
        import pygame as pg
        pg.init()
        print("   ✅ Pygame initialized")
        
        # Test app creation
        print("4. Creating TrafficApp...")
        app = TrafficApp()
        print("   ✅ TrafficApp created successfully")
        
        # Test running briefly
        print("5. Testing brief run...")
        app.run()
        print("   ✅ App ran (may have closed normally)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging main application...")
    print("=" * 50)
    
    success = test_app_initialization()
    
    print()
    print("=" * 50)
    if success:
        print("✅ App initialization test completed.")
        print("If the app window closed immediately, it might be a normal exit or pygame issue.")
    else:
        print("❌ App initialization failed. Check the errors above.")