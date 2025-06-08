#!/usr/bin/env python3
"""
Cache Validation Test for VRCPhoto2URL Server
Tests cache effectiveness with actual file data
"""

import asyncio
import time
import json
import tempfile
import os
from pathlib import Path
import aiohttp
import aiofiles
import colorama
from colorama import Fore, Style

# Initialize colorama for colored output
colorama.init()

class CacheValidationTest:
    def __init__(self, base_url: str = "http://localhost:8001", api_key: str = "your-secret-api-key-change-this"):
        self.base_url = base_url
        self.api_key = api_key
        self.session: aiohttp.ClientSession = None
        self.uploaded_files = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.api_key}'},
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up uploaded files
        for file_id in self.uploaded_files:
            try:
                await self.session.delete(f"{self.base_url}/files/{file_id}")
            except:
                pass
        
        if self.session:
            await self.session.close()
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{title:^60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    
    def print_test(self, test_name: str, status: str, duration: float, details: str = ""):
        """Print test result with color coding"""
        if status == "PASS":
            color = Fore.GREEN
            symbol = "✅"
        elif status == "FAIL":
            color = Fore.RED
            symbol = "❌"
        else:  # WARN
            color = Fore.YELLOW
            symbol = "⚠️"
        
        print(f"{symbol} {color}{test_name:<40}{Style.RESET_ALL} {duration:>6.3f}s {details}")
    
    async def create_test_files(self, count: int = 5) -> bool:
        """Create test files for cache validation"""
        self.print_header("📁 CREATING TEST FILES")
        
        try:
            for i in range(count):
                # Create test file content
                content = f"Test file content {i} - " + "x" * (1000 + i * 500)  # Variable sizes
                
                # Upload test file
                data = aiohttp.FormData()
                data.add_field('file', 
                             content.encode(), 
                             filename=f'test_cache_{i}.txt',
                             content_type='text/plain')
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/upload", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.uploaded_files.append(result['file_id'])
                        duration = time.time() - start_time
                        self.print_test(f"Upload Test File {i+1}", "PASS", duration, f"ID: {result['file_id'][:8]}")
                    else:
                        self.print_test(f"Upload Test File {i+1}", "FAIL", time.time() - start_time, f"Status: {response.status}")
                        return False
            
            print(f"\n{Fore.GREEN}✅ Successfully created {count} test files{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Failed to create test files: {e}{Style.RESET_ALL}")
            return False
    
    async def test_cache_invalidation(self) -> bool:
        """Test that cache is properly invalidated on file operations"""
        self.print_header("🔄 CACHE INVALIDATION TEST")
        
        try:
            # Get initial stats (should populate cache)
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/stats") as response:
                initial_stats = await response.json()
            initial_time = time.time() - start_time
            self.print_test("Initial Stats Request", "PASS", initial_time, f"Files: {initial_stats['total_files']}")
            
            # Upload a new file
            content = "Cache invalidation test file"
            data = aiohttp.FormData()
            data.add_field('file', 
                         content.encode(), 
                         filename='cache_test.txt',
                         content_type='text/plain')
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    new_file_id = result['file_id']
                    self.uploaded_files.append(new_file_id)
                    upload_time = time.time() - start_time
                    self.print_test("Upload New File", "PASS", upload_time, f"ID: {new_file_id[:8]}")
                else:
                    self.print_test("Upload New File", "FAIL", time.time() - start_time, f"Status: {response.status}")
                    return False
            
            # Get stats again (should reflect new file)
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/stats") as response:
                updated_stats = await response.json()
            updated_time = time.time() - start_time
            
            # Verify cache was invalidated
            if updated_stats['total_files'] > initial_stats['total_files']:
                self.print_test("Stats After Upload", "PASS", updated_time, f"Files: {updated_stats['total_files']} (+{updated_stats['total_files'] - initial_stats['total_files']})")
                
                # Delete the file
                start_time = time.time()
                async with self.session.delete(f"{self.base_url}/files/{new_file_id}") as response:
                    if response.status == 200:
                        delete_time = time.time() - start_time
                        self.print_test("Delete File", "PASS", delete_time, f"ID: {new_file_id[:8]}")
                        self.uploaded_files.remove(new_file_id)
                    else:
                        self.print_test("Delete File", "FAIL", time.time() - start_time, f"Status: {response.status}")
                        return False
                
                # Get stats again (should reflect deletion)
                start_time = time.time()
                async with self.session.get(f"{self.base_url}/stats") as response:
                    final_stats = await response.json()
                final_time = time.time() - start_time
                
                if final_stats['total_files'] == initial_stats['total_files']:
                    self.print_test("Stats After Delete", "PASS", final_time, f"Files: {final_stats['total_files']} (restored)")
                    return True
                else:
                    self.print_test("Stats After Delete", "FAIL", final_time, f"Expected: {initial_stats['total_files']}, Got: {final_stats['total_files']}")
                    return False
            else:
                self.print_test("Stats After Upload", "FAIL", updated_time, "File count not updated - cache not invalidated")
                return False
                
        except Exception as e:
            print(f"\n{Fore.RED}❌ Cache invalidation test failed: {e}{Style.RESET_ALL}")
            return False
    
    async def test_cache_performance_with_data(self) -> bool:
        """Test cache performance with actual file data"""
        self.print_header("⚡ CACHE PERFORMANCE WITH DATA")
        
        try:
            # Clear any existing cache by waiting for TTL + margin
            print(f"{Fore.YELLOW}⏳ Waiting 35s for cache to expire...{Style.RESET_ALL}")
            await asyncio.sleep(35)
            
            # Cold cache request (will read from disk)
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/stats") as response:
                cold_stats = await response.json()
            cold_time = time.time() - start_time
            self.print_test("Cold Cache Request", "INFO", cold_time, f"Files: {cold_stats['total_files']}")
            
            # Warm cache requests (should use cache)
            warm_times = []
            for i in range(5):
                start_time = time.time()
                async with self.session.get(f"{self.base_url}/stats") as response:
                    await response.json()
                warm_times.append(time.time() - start_time)
                await asyncio.sleep(0.1)  # Small delay between requests
            
            avg_warm_time = sum(warm_times) / len(warm_times)
            improvement = (cold_time - avg_warm_time) / cold_time * 100 if cold_time > 0 else 0
            
            if improvement > 0:
                status = "PASS" if improvement > 10 else "WARN"
                self.print_test("Warm Cache Average", status, avg_warm_time, f"improvement: {improvement:.1f}%")
                return status == "PASS"
            else:
                self.print_test("Warm Cache Average", "WARN", avg_warm_time, "no improvement detected")
                return False
                
        except Exception as e:
            print(f"\n{Fore.RED}❌ Cache performance test failed: {e}{Style.RESET_ALL}")
            return False
    
    async def run_cache_validation_suite(self):
        """Run the complete cache validation test suite"""
        print(f"{Fore.MAGENTA}🔍 VRCPhoto2URL Cache Validation Test Suite{Style.RESET_ALL}")
        print(f"Testing server: {self.base_url}")
        
        # Test server connectivity
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    self.print_test("Server Connectivity", "PASS", 0.0, "✅ Online")
                else:
                    self.print_test("Server Connectivity", "FAIL", 0.0, f"❌ Status: {response.status}")
                    return
        except Exception as e:
            self.print_test("Server Connectivity", "FAIL", 0.0, f"❌ {str(e)}")
            return
        
        # Create test files
        if not await self.create_test_files(5):
            return
        
        # Test cache invalidation
        cache_invalidation_ok = await self.test_cache_invalidation()
        
        # Test cache performance with actual data
        cache_performance_ok = await self.test_cache_performance_with_data()
        
        # Summary
        self.print_header("📋 CACHE VALIDATION SUMMARY")
        
        if cache_invalidation_ok and cache_performance_ok:
            print(f"{Fore.GREEN}✅ All cache validation tests passed!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🎉 Cache system is working correctly and providing performance benefits{Style.RESET_ALL}")
        elif cache_invalidation_ok:
            print(f"{Fore.YELLOW}⚠️ Cache invalidation works but performance improvement is minimal{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 This may be normal for small datasets or very fast storage{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Cache validation failed - check implementation{Style.RESET_ALL}")

async def main():
    """Main test execution"""
    async with CacheValidationTest() as test_suite:
        await test_suite.run_cache_validation_suite()

if __name__ == "__main__":
    asyncio.run(main())
