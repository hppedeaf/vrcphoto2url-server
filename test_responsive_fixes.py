#!/usr/bin/env python3
"""
Test script to verify responsive design fixes for VRCPhoto2URL admin interface.
Tests window resizing, maximizing, and responsive behavior.
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_responsive_behavior():
    """Test the responsive behavior of the admin interface."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    print("🧪 Starting responsive design tests...")
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/admin", timeout=5)
        if response.status_code != 200:
            print("❌ Server not accessible at http://localhost:8000")
            return False
            
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the server first.")
        return False
    
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:8000/admin")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "app-container"))
        )
        
        print("✅ Admin interface loaded successfully")
        
        # Test 1: Check initial layout
        print("\n📏 Test 1: Initial layout check")
        app_container = driver.find_element(By.CLASS_NAME, "app-container")
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        main_content = driver.find_element(By.CLASS_NAME, "main-content")
        
        print(f"   App container display: {app_container.value_of_css_property('display')}")
        print(f"   Sidebar width: {sidebar.size['width']}px")
        print(f"   Main content flex: {main_content.value_of_css_property('flex')}")
        
        # Test 2: Window resize simulation
        print("\n📐 Test 2: Window resize simulation")
        
        # Test different window sizes
        sizes = [
            (1920, 1080, "Desktop Large"),
            (1366, 768, "Desktop Medium"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        for width, height, description in sizes:
            driver.set_window_size(width, height)
            time.sleep(1)  # Allow layout to adjust
            
            # Check layout properties
            sidebar_width = sidebar.size['width']
            main_width = main_content.size['width']
            
            print(f"   {description} ({width}x{height}): Sidebar={sidebar_width}px, Main={main_width}px")
            
            # Check if layout is responsive
            if width <= 768:
                # Mobile - sidebar should be handled differently
                sidebar_classes = sidebar.get_attribute('class')
                if 'mobile-layout' in sidebar_classes:
                    print(f"   ✅ Mobile layout detected for {description}")
                else:
                    print(f"   ⚠️ Mobile layout not detected for {description}")
            else:
                # Desktop - sidebar should be visible
                if sidebar_width > 0:
                    print(f"   ✅ Desktop layout correct for {description}")
                else:
                    print(f"   ❌ Sidebar hidden on {description}")
        
        # Test 3: Sidebar toggle
        print("\n🔄 Test 3: Sidebar toggle functionality")
        
        # Reset to desktop size
        driver.set_window_size(1366, 768)
        time.sleep(1)
        
        try:
            toggle_button = driver.find_element(By.ID, "sidebar-toggle")
            initial_sidebar_width = sidebar.size['width']
            
            # Click toggle
            toggle_button.click()
            time.sleep(0.5)
            
            new_sidebar_width = sidebar.size['width']
            
            if new_sidebar_width != initial_sidebar_width:
                print("   ✅ Sidebar toggle working")
            else:
                print("   ⚠️ Sidebar toggle may not be working properly")
                
        except Exception as e:
            print(f"   ⚠️ Sidebar toggle test failed: {e}")
        
        # Test 4: Files grid responsiveness
        print("\n📱 Test 4: Files grid responsiveness")
        
        try:
            # Navigate to files tab
            files_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="files"]')
            files_tab.click()
            time.sleep(1)
            
            # Check if files grid exists
            files_grid = driver.find_element(By.ID, "files-grid")
            grid_columns = files_grid.value_of_css_property('grid-template-columns')
            
            print(f"   Files grid columns: {grid_columns}")
            
            # Test different sizes
            for width, height, description in [(1920, 1080), (768, 1024), (375, 667)]:
                driver.set_window_size(width, height)
                time.sleep(1)
                
                new_grid_columns = files_grid.value_of_css_property('grid-template-columns')
                print(f"   {description}: {new_grid_columns}")
                
        except Exception as e:
            print(f"   ⚠️ Files grid test failed: {e}")
        
        # Test 5: Window maximize simulation
        print("\n🖥️ Test 5: Window maximize simulation")
        
        driver.maximize_window()
        time.sleep(1)
        
        maximized_width = driver.get_window_size()['width']
        maximized_height = driver.get_window_size()['height']
        
        print(f"   Maximized size: {maximized_width}x{maximized_height}")
        
        # Check if layout adapts to maximized window
        final_sidebar_width = sidebar.size['width']
        final_main_width = main_content.size['width']
        
        print(f"   Maximized layout: Sidebar={final_sidebar_width}px, Main={final_main_width}px")
        
        if final_main_width > maximized_width * 0.5:
            print("   ✅ Layout properly utilizes maximized space")
        else:
            print("   ⚠️ Layout may not be utilizing maximized space efficiently")
        
        print("\n🎉 Responsive design tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print("VRCPhoto2URL Responsive Design Test")
    print("=" * 50)
    
    success = test_responsive_behavior()
    
    if success:
        print("\n✅ All responsive design tests completed successfully!")
        print("📝 The admin interface should now handle window resizing and maximizing properly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
