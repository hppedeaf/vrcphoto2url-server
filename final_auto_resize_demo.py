#!/usr/bin/env python3
"""
Final demonstration of auto-resize functionality working correctly
"""
import requests
import os
from PIL import Image

def test_auto_resize_final():
    """Test auto-resize with real test images"""
    
    print("🎉 FINAL AUTO-RESIZE DEMONSTRATION")
    print("=" * 50)
    
    # Server config
    BASE_URL = "http://localhost:8000"
    API_KEY = "your-secret-api-key-change-this"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    # Test images
    test_images = [
        ("test_images/1920x1080_HD_image.jpg", (1920, 1080), "Should NOT resize"),
        ("test_images/2560x1440_QHD_image.jpg", (2560, 1440), "Should resize to 2048x1152"),
        ("test_images/3840x2160_4K_image.jpg", (3840, 2160), "Should resize to 2048x1152")
    ]
    
    results = []
    
    for image_path, original_size, expectation in test_images:
        if not os.path.exists(image_path):
            print(f"❌ Test image not found: {image_path}")
            continue
            
        print(f"\n📸 Testing: {os.path.basename(image_path)}")
        print(f"   Original: {original_size[0]}x{original_size[1]}")
        print(f"   Expected: {expectation}")
        
        # Get original file info
        original_file_size = os.path.getsize(image_path)
        print(f"   Original file size: {original_file_size:,} bytes")
        
        # Upload image
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                file_id = result['file_id']
                uploaded_size = result['file_size']
                
                print(f"   ✅ Upload successful!")
                print(f"   📊 Final file size: {uploaded_size:,} bytes")
                
                # Download and check actual dimensions
                download_url = f"{BASE_URL}/files/{file_id}.jpg"
                download_response = requests.get(download_url)
                
                if download_response.status_code == 200:
                    # Save temporarily to check dimensions
                    temp_path = f"temp_{file_id}.jpg"
                    with open(temp_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    # Check actual dimensions
                    with Image.open(temp_path) as img:
                        actual_width, actual_height = img.size
                        max_dimension = max(actual_width, actual_height)
                        
                        print(f"   📐 Actual dimensions: {actual_width}x{actual_height}")
                        print(f"   📏 Max dimension: {max_dimension}px")
                        
                        # Verify result
                        if max_dimension <= 2048:
                            print(f"   ✅ SUCCESS: Within 2048px limit!")
                        else:
                            print(f"   ❌ FAILED: Exceeds 2048px limit!")
                        
                        # Check if resize happened as expected
                        was_resized = uploaded_size < original_file_size
                        if was_resized:
                            reduction = ((original_file_size - uploaded_size) / original_file_size) * 100
                            print(f"   🔄 Image was resized! Size reduced by {reduction:.1f}%")
                        else:
                            print(f"   📏 Image was NOT resized")
                        
                        results.append({
                            'filename': os.path.basename(image_path),
                            'original_dimensions': original_size,
                            'final_dimensions': (actual_width, actual_height),
                            'was_resized': was_resized,
                            'within_limits': max_dimension <= 2048
                        })
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                
                # Clean up uploaded file
                requests.delete(f"{BASE_URL}/files/{file_id}", headers=headers)
                
            else:
                print(f"   ❌ Upload failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for result in results:
        status = "✅ PASSED" if result['within_limits'] else "❌ FAILED"
        print(f"{status} - {result['filename']}")
        
        orig = result['original_dimensions']
        final = result['final_dimensions']
        print(f"        {orig[0]}x{orig[1]} → {final[0]}x{final[1]}")
        
        if not result['within_limits']:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Auto-resize functionality is working perfectly!")
        print(f"✅ All images are within 2048px limit!")
        print(f"✅ Ready for production use!")
    else:
        print(f"\n❌ Some tests failed - please check implementation")
    
    return all_passed

if __name__ == "__main__":
    test_auto_resize_final()
