#!/usr/bin/env python3
"""
Test 100 urządzeń jednocześnie - sprawdza skalowalność aplikacji
Symuluje 100 różnych urządzeń (telefony, tablety, komputery, laptopy) jednocześnie
"""
import requests
import time
import statistics
import json
import random
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse


class DeviceSimulator:
    """Symulator urządzenia"""
    
    def __init__(self, device_type: str, device_id: str, base_url: str = "http://localhost:8000"):
        self.device_type = device_type
        self.device_id = device_id
        self.base_url = base_url
        self.session = requests.Session()
        
        # Symuluj różne User-Agent dla różnych urządzeń
        user_agents = {
            "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "tablet": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "laptop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        self.session.headers.update({
            'User-Agent': user_agents.get(device_type, user_agents["desktop"]),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        self.user_id = None
        self.trip_id = None
        self.created_resources = []
    
    def create_user(self) -> bool:
        """Tworzy użytkownika dla tego urządzenia"""
        user_data = {
            "name": f"{self.device_type.capitalize()}User_{self.device_id}",
            "email": f"{self.device_type}_{self.device_id}_{int(time.time())}@example.com",
            "password": "password123"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/users/", json=user_data, timeout=10)
            if response.status_code in [200, 201]:
                self.user_id = response.json()["_id"]
                self.created_resources.append(("user", self.user_id))
                return True
            return False
        except Exception as e:
            print(f"❌ {self.device_type} {self.device_id}: Błąd tworzenia użytkownika: {e}")
            return False
    
    def create_trip(self) -> bool:
        """Tworzy podróż dla tego urządzenia"""
        if not self.user_id:
            return False
        
        destinations = ["Paris", "London", "Tokyo", "New York", "Rome", "Barcelona", "Amsterdam", "Berlin", "Vienna", "Prague"]
        
        trip_data = {
            "name": f"{self.device_type.capitalize()} Trip {self.device_id}",
            "trip_name": f"{self.device_type.capitalize()} Trip {self.device_id}",
            "destination": random.choice(destinations),
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "budget": random.randint(1000, 5000),
            "travelers": random.randint(1, 4),
            "user_id": self.user_id,
            "created_at": "2024-01-01T00:00:00Z",
            "status": "planning"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/trips/", json=trip_data, timeout=10)
            if response.status_code in [200, 201]:
                self.trip_id = response.json()["_id"]
                self.created_resources.append(("trip", self.trip_id))
                return True
            return False
        except Exception as e:
            print(f"❌ {self.device_type} {self.device_id}: Błąd tworzenia podróży: {e}")
            return False
    
    def run_basic_workflow(self) -> Dict:
        """Uruchamia podstawowy workflow (tylko user + trip)"""
        start_time = time.time()
        
        # 1. Tworzenie użytkownika
        user_created = self.create_user()
        user_time = time.time() - start_time
        
        # 2. Tworzenie podróży
        trip_start = time.time()
        trip_created = self.create_trip() if user_created else False
        trip_time = time.time() - trip_start
        
        total_time = time.time() - start_time
        
        return {
            "device_type": self.device_type,
            "device_id": self.device_id,
            "user_created": user_created,
            "user_time": user_time,
            "trip_created": trip_created,
            "trip_time": trip_time,
            "total_time": total_time,
            "success": user_created and trip_created
        }


class HundredDeviceTester:
    """Tester 100 urządzeń jednocześnie"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def check_app_availability(self) -> bool:
        """Sprawdza czy aplikacja jest dostępna"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_device_simulators(self, num_devices: int = 100) -> List[DeviceSimulator]:
        """Tworzy symulatory różnych urządzeń"""
        device_types = ["mobile", "tablet", "desktop", "laptop"]
        devices = []
        
        for i in range(num_devices):
            device_type = device_types[i % len(device_types)]
            device_id = f"device_{i+1}"
            devices.append(DeviceSimulator(device_type, device_id, self.base_url))
        
        return devices
    
    def test_100_devices(self, num_devices: int = 100) -> Dict:
        """Test 100 urządzeń jednocześnie"""
        print(f"\n🚀 TEST 100 URZĄDZEŃ JEDNOCZEŚNIE")
        print("=" * 60)
        print(f"Liczba urządzeń: {num_devices}")
        print(f"Host: {self.base_url}")
        print("=" * 60)
        
        devices = self.create_device_simulators(num_devices)
        
        # Uruchom testy równolegle z ograniczeniem wątków
        start_time = time.time()
        results = []
        successful_count = 0
        
        # Użyj ThreadPoolExecutor z ograniczeniem wątków
        max_workers = min(50, num_devices)  # Maksymalnie 50 wątków jednocześnie
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Uruchom workflow dla każdego urządzenia
            future_to_device = {
                executor.submit(device.run_basic_workflow): device 
                for device in devices
            }
            
            completed = 0
            for future in as_completed(future_to_device):
                device = future_to_device[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    if result["success"]:
                        successful_count += 1
                    
                    # Wyświetl postęp co 10 urządzeń
                    if completed % 10 == 0:
                        print(f"📊 Postęp: {completed}/{num_devices} urządzeń ({successful_count} udanych)")
                        
                except Exception as e:
                    print(f"❌ {device.device_type} {device.device_id}: Błąd - {e}")
                    results.append({
                        "device_type": device.device_type,
                        "device_id": device.device_id,
                        "success": False,
                        "error": str(e)
                    })
        
        total_time = time.time() - start_time
        
        # Analiza wyników
        failed_count = num_devices - successful_count
        success_rate = successful_count / num_devices * 100
        
        # Statystyki według typu urządzenia
        device_stats = self._analyze_device_results(results)
        
        # Statystyki czasowe
        time_stats = self._analyze_time_results(results)
        
        return {
            "total_devices": num_devices,
            "successful_devices": successful_count,
            "failed_devices": failed_count,
            "success_rate": success_rate,
            "total_time": total_time,
            "device_stats": device_stats,
            "time_stats": time_stats,
            "results": results
        }
    
    def _analyze_device_results(self, results: List[Dict]) -> Dict:
        """Analizuje wyniki według typu urządzenia"""
        device_types = {}
        
        for result in results:
            device_type = result["device_type"]
            if device_type not in device_types:
                device_types[device_type] = {"total": 0, "successful": 0, "times": []}
            
            device_types[device_type]["total"] += 1
            if result.get("success", False):
                device_types[device_type]["successful"] += 1
            if "total_time" in result:
                device_types[device_type]["times"].append(result["total_time"])
        
        # Oblicz statystyki dla każdego typu urządzenia
        for device_type in device_types:
            stats = device_types[device_type]
            stats["success_rate"] = stats["successful"] / stats["total"] * 100
            if stats["times"]:
                stats["avg_time"] = statistics.mean(stats["times"])
                stats["min_time"] = min(stats["times"])
                stats["max_time"] = max(stats["times"])
                stats["median_time"] = statistics.median(stats["times"])
            else:
                stats["avg_time"] = 0
                stats["min_time"] = 0
                stats["max_time"] = 0
                stats["median_time"] = 0
        
        return device_types
    
    def _analyze_time_results(self, results: List[Dict]) -> Dict:
        """Analizuje statystyki czasowe"""
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            return {"error": "No successful results"}
        
        times = [r["total_time"] for r in successful_results]
        
        return {
            "avg_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "min_time": min(times),
            "max_time": max(times),
            "p95_time": self._percentile(times, 95),
            "p99_time": self._percentile(times, 99),
            "total_successful": len(successful_results)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Oblicza percentyl"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def run_test(self, num_devices: int = 100):
        """Uruchamia test 100 urządzeń"""
        print("🧪 TEST SKALOWALNOŚCI - 100 URZĄDZEŃ JEDNOCZEŚNIE")
        print("=" * 60)
        
        # Sprawdź dostępność aplikacji
        if not self.check_app_availability():
            print("❌ Aplikacja nie jest dostępna na", self.base_url)
            return
        
        print("✅ Aplikacja jest dostępna")
        
        # Uruchom test
        results = self.test_100_devices(num_devices)
        
        # Wyświetl wyniki
        self._print_results(results)
        
        return results
    
    def _print_results(self, results: Dict):
        """Wyświetla wyniki testów"""
        print(f"\n{'='*60}")
        print("📊 WYNIKI TESTU 100 URZĄDZEŃ")
        print(f"{'='*60}")
        
        print(f"\n🖥️  STATYSTYKI OGÓLNE:")
        print(f"   Łączna liczba urządzeń: {results['total_devices']}")
        print(f"   Udane urządzenia: {results['successful_devices']}")
        print(f"   Nieudane urządzenia: {results['failed_devices']}")
        print(f"   Wskaźnik sukcesu: {results['success_rate']:.1f}%")
        print(f"   Całkowity czas: {results['total_time']:.2f}s")
        
        # Statystyki czasowe
        if "time_stats" in results and "error" not in results["time_stats"]:
            time_stats = results["time_stats"]
            print(f"\n⏱️  STATYSTYKI CZASOWE:")
            print(f"   Średni czas: {time_stats['avg_time']:.2f}s")
            print(f"   Mediana: {time_stats['median_time']:.2f}s")
            print(f"   Min/Max: {time_stats['min_time']:.2f}s / {time_stats['max_time']:.2f}s")
            print(f"   P95: {time_stats['p95_time']:.2f}s")
            print(f"   P99: {time_stats['p99_time']:.2f}s")
        
        # Statystyki według typu urządzenia
        print(f"\n📱 STATYSTYKI WEDŁUG TYPU URZĄDZENIA:")
        for device_type, stats in results['device_stats'].items():
            print(f"   {device_type.capitalize()}:")
            print(f"     Liczba: {stats['total']}")
            print(f"     Sukces: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
            print(f"     Średni czas: {stats['avg_time']:.2f}s")
            print(f"     Mediana: {stats['median_time']:.2f}s")
            print(f"     Min/Max: {stats['min_time']:.2f}s / {stats['max_time']:.2f}s")
        
        # Rekomendacje
        print(f"\n💡 REKOMENDACJE:")
        if results['success_rate'] >= 95:
            print("🎉 Aplikacja doskonale obsługuje 100 urządzeń jednocześnie!")
            print("✅ Gotowa na produkcję z wysokim obciążeniem!")
        elif results['success_rate'] >= 90:
            print("✅ Aplikacja dobrze obsługuje 100 urządzeń.")
            print("⚠️  Można wdrażać na produkcję z monitoringiem.")
        elif results['success_rate'] >= 80:
            print("⚠️  Aplikacja ma problemy z obsługą 100 urządzeń.")
            print("🔧 Wymagana optymalizacja przed wdrożeniem.")
        else:
            print("🚨 Aplikacja ma poważne problemy z obsługą 100 urządzeń!")
            print("🚨 Wymagana natychmiastowa optymalizacja!")
        
        # Sprawdź różnice między typami urządzeń
        device_types = list(results['device_stats'].keys())
        if len(device_types) > 1:
            success_rates = [results['device_stats'][dt]['success_rate'] for dt in device_types]
            if max(success_rates) - min(success_rates) > 10:
                print("⚠️  Znaczne różnice w wydajności między typami urządzeń!")
                print("🔧 Sprawdź optymalizację dla słabszych urządzeń.")
            else:
                print("✅ Równomierna wydajność na wszystkich typach urządzeń!")


def main():
    """Główna funkcja"""
    parser = argparse.ArgumentParser(description="Test 100 urządzeń jednocześnie")
    parser.add_argument("--host", default="http://localhost:8000", help="Host aplikacji")
    parser.add_argument("--devices", type=int, default=100, help="Liczba urządzeń do testowania")
    
    args = parser.parse_args()
    
    tester = HundredDeviceTester(args.host)
    tester.run_test(args.devices)


if __name__ == "__main__":
    main()
