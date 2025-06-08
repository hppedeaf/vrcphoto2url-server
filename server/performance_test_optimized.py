#!/usr/bin/env python3
"""
Performance Test Script for VRCPhoto2URL Server - Optimized Version
Tests caching improvements and performance enhancements
"""

import asyncio
import time
import json
import statistics
from typing import List, Dict, Any
import aiohttp
import colorama
from colorama import Fore, Style

# Initialize colorama for colored output
colorama.init()

class PerformanceTestSuite:
    def __init__(self, base_url: str = "http://localhost:8001", api_key: str = "your-secret-api-key-change-this"):
        self.base_url = base_url
        self.api_key = api_key
        self.session: aiohttp.ClientSession = None
        self.results: List[Dict[str, Any]] = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.api_key}'},
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
        
        print(f"{symbol} {color}{test_name:<35}{Style.RESET_ALL} {duration:>6.3f}s {details}")
    
    async def test_endpoint_performance(self, endpoint: str, test_name: str, 
                                      expected_max_time: float = 2.0, 
                                      iterations: int = 5) -> Dict[str, Any]:
        """Test endpoint performance over multiple iterations"""
        times = []
        errors = 0
        
        for i in range(iterations):
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        await response.json()  # Consume response
                        duration = time.time() - start_time
                        times.append(duration)
                    else:
                        errors += 1
                        duration = time.time() - start_time
                        times.append(duration)
            except Exception as e:
                errors += 1
                duration = time.time() - start_time
                times.append(duration)
                
            # Small delay between requests to simulate real usage
            await asyncio.sleep(0.1)
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)
            
            # Determine status
            if errors > 0:
                status = "FAIL"
            elif avg_time <= expected_max_time:
                status = "PASS"
            else:
                status = "WARN"
            
            details = f"avg:{avg_time:.3f}s min:{min_time:.3f}s max:{max_time:.3f}s"
            self.print_test(test_name, status, avg_time, details)
            
            result = {
                "test_name": test_name,
                "endpoint": endpoint,
                "status": status,
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "median_time": median_time,
                "errors": errors,
                "iterations": iterations
            }
            
            self.results.append(result)
            return result
        else:
            self.print_test(test_name, "FAIL", 0.0, "No successful requests")
            return {"test_name": test_name, "status": "FAIL", "avg_time": 0}
    
    async def test_cache_effectiveness(self) -> Dict[str, Any]:
        """Test cache effectiveness by making rapid sequential requests"""
        self.print_header("🚀 CACHE EFFECTIVENESS TEST")
        
        # First request (cold cache)
        start_time = time.time()
        async with self.session.get(f"{self.base_url}/stats") as response:
            await response.json()
        cold_time = time.time() - start_time
        
        # Wait a moment then make rapid requests (warm cache)
        await asyncio.sleep(0.1)
        warm_times = []
        
        for i in range(10):
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/stats") as response:
                await response.json()
            warm_times.append(time.time() - start_time)
            await asyncio.sleep(0.05)  # Very short delay
        
        avg_warm_time = statistics.mean(warm_times)
        improvement = (cold_time - avg_warm_time) / cold_time * 100
        
        if improvement > 50:  # Cache should provide significant improvement
            status = "PASS"
        elif improvement > 20:
            status = "WARN"
        else:
            status = "FAIL"
        
        self.print_test("Cold Cache Request", "INFO", cold_time)
        self.print_test("Warm Cache Average", status, avg_warm_time, f"improvement: {improvement:.1f}%")
        
        return {
            "cold_time": cold_time,
            "warm_time": avg_warm_time,
            "improvement_percent": improvement,
            "status": status
        }
    
    async def test_concurrent_load(self, endpoint: str = "/stats", concurrency: int = 10) -> Dict[str, Any]:
        """Test concurrent request handling"""
        self.print_header(f"🔄 CONCURRENT LOAD TEST ({concurrency} simultaneous requests)")
        
        async def single_request():
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        await response.json()
                        return time.time() - start_time, True
                    else:
                        return time.time() - start_time, False
            except Exception:
                return time.time() - start_time, False
        
        # Execute concurrent requests
        start_time = time.time()
        tasks = [single_request() for _ in range(concurrency)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze results
        successful_times = [r[0] for r in results if isinstance(r, tuple) and r[1]]
        failed_count = len([r for r in results if not (isinstance(r, tuple) and r[1])])
        
        if successful_times:
            avg_response_time = statistics.mean(successful_times)
            max_response_time = max(successful_times)
            success_rate = len(successful_times) / concurrency * 100
            
            # Determine status
            if success_rate >= 95 and avg_response_time <= 2.0:
                status = "PASS"
            elif success_rate >= 80 and avg_response_time <= 3.0:
                status = "WARN"
            else:
                status = "FAIL"
            
            details = f"success: {success_rate:.1f}% max: {max_response_time:.3f}s"
            self.print_test(f"Concurrent Load ({concurrency})", status, avg_response_time, details)
            
            return {
                "concurrency": concurrency,
                "total_time": total_time,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "success_rate": success_rate,
                "failed_count": failed_count,
                "status": status
            }
        else:
            self.print_test(f"Concurrent Load ({concurrency})", "FAIL", total_time, "All requests failed")
            return {"status": "FAIL", "concurrency": concurrency}
    
    async def run_complete_test_suite(self):
        """Run the complete performance test suite"""
        print(f"{Fore.MAGENTA}🎯 VRCPhoto2URL Performance Test Suite - Optimized Version{Style.RESET_ALL}")
        print(f"Testing server: {self.base_url}")
        
        # Test server connectivity first
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
        
        # Core performance tests
        self.print_header("📊 CORE ENDPOINT PERFORMANCE")
        await self.test_endpoint_performance("/stats", "Stats Endpoint", 1.5, 5)
        await self.test_endpoint_performance("/admin/stats", "Admin Stats Endpoint", 1.5, 5)
        await self.test_endpoint_performance("/files", "Files List Endpoint", 2.0, 5)
        await self.test_endpoint_performance("/health", "Health Check", 0.5, 5)
        
        # Cache effectiveness test
        cache_result = await self.test_cache_effectiveness()
        
        # Concurrent load tests
        await self.test_concurrent_load("/stats", 5)
        await self.test_concurrent_load("/stats", 10)
        await self.test_concurrent_load("/admin/stats", 5)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("📋 TEST SUMMARY")
        
        if not self.results:
            print(f"{Fore.RED}No test results to summarize{Style.RESET_ALL}")
            return
        
        passed = len([r for r in self.results if r.get('status') == 'PASS'])
        warned = len([r for r in self.results if r.get('status') == 'WARN'])
        failed = len([r for r in self.results if r.get('status') == 'FAIL'])
        total = len(self.results)
        
        # Calculate overall performance metrics
        avg_times = [r.get('avg_time', 0) for r in self.results if r.get('avg_time')]
        if avg_times:
            overall_avg = statistics.mean(avg_times)
            best_time = min(avg_times)
            worst_time = max(avg_times)
        else:
            overall_avg = best_time = worst_time = 0
        
        # Performance grade
        if passed / total >= 0.9 and overall_avg <= 1.5:
            grade = f"{Fore.GREEN}A+ (Excellent){Style.RESET_ALL}"
        elif passed / total >= 0.8 and overall_avg <= 2.0:
            grade = f"{Fore.GREEN}A (Very Good){Style.RESET_ALL}"
        elif passed / total >= 0.7 and overall_avg <= 3.0:
            grade = f"{Fore.YELLOW}B (Good){Style.RESET_ALL}"
        elif passed / total >= 0.6:
            grade = f"{Fore.YELLOW}C (Acceptable){Style.RESET_ALL}"
        else:
            grade = f"{Fore.RED}F (Needs Improvement){Style.RESET_ALL}"
        
        print(f"📊 Test Results: {Fore.GREEN}{passed} passed{Style.RESET_ALL}, "
              f"{Fore.YELLOW}{warned} warnings{Style.RESET_ALL}, "
              f"{Fore.RED}{failed} failed{Style.RESET_ALL} ({total} total)")
        print(f"⚡ Performance: Avg {overall_avg:.3f}s, Best {best_time:.3f}s, Worst {worst_time:.3f}s")
        print(f"🎖️ Overall Grade: {grade}")
        
        # Recommendations
        if overall_avg > 2.0:
            print(f"\n{Fore.YELLOW}💡 Recommendations:{Style.RESET_ALL}")
            print("   • Consider increasing cache TTL")
            print("   • Review file system performance")
            print("   • Consider database optimization")
        elif overall_avg < 1.0:
            print(f"\n{Fore.GREEN}🎉 Excellent performance! Server is well optimized.{Style.RESET_ALL}")

async def main():
    """Main test execution"""
    async with PerformanceTestSuite() as test_suite:
        await test_suite.run_complete_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
