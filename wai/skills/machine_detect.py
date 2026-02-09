"""
Machine Detection Skill - Detect hardware specs and create machine profile lugs.

This skill detects the current machine's hardware capabilities and creates
a machine profile lug that can be stored in the hub for cross-wheel optimization.

Usage:
    wai detect-machine [--save-to-hub]
"""

import platform
import subprocess
import json
import socket
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class MachineDetector:
    """Detect machine hardware specifications."""

    def __init__(self):
        self.hostname = socket.gethostname()
        self.platform = platform.system()

    def detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information."""
        cpu_info = {
            'model': 'Unknown',
            'cores': platform.machine(),
            'threads': 0,
            'architecture': platform.machine()
        }

        if self.platform == 'Linux':
            try:
                # Get CPU model and cores from /proc/cpuinfo
                with open('/proc/cpuinfo', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'model name' in line.lower():
                            cpu_info['model'] = line.split(':')[1].strip()
                            break

                # Count logical processors
                cpu_info['threads'] = sum(1 for line in lines if 'processor' in line.lower())

                # Get physical cores
                cores_result = subprocess.run(
                    ['lscpu'], capture_output=True, text=True, timeout=5
                )
                for line in cores_result.stdout.split('\n'):
                    if 'Core(s) per socket' in line:
                        cores_per_socket = int(line.split(':')[1].strip())
                    if 'Socket(s)' in line:
                        sockets = int(line.split(':')[1].strip())
                        cpu_info['cores'] = cores_per_socket * sockets

            except Exception as e:
                cpu_info['error'] = str(e)

        elif self.platform == 'Darwin':  # macOS
            try:
                result = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True, text=True, timeout=5
                )
                cpu_info['model'] = result.stdout.strip()

                result = subprocess.run(
                    ['sysctl', '-n', 'hw.physicalcpu'],
                    capture_output=True, text=True, timeout=5
                )
                cpu_info['cores'] = int(result.stdout.strip())

                result = subprocess.run(
                    ['sysctl', '-n', 'hw.logicalcpu'],
                    capture_output=True, text=True, timeout=5
                )
                cpu_info['threads'] = int(result.stdout.strip())

            except Exception as e:
                cpu_info['error'] = str(e)

        elif self.platform == 'Windows':
            try:
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'name'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    cpu_info['model'] = lines[1].strip()

                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'NumberOfCores'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    cpu_info['cores'] = int(lines[1].strip())

                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'NumberOfLogicalProcessors'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    cpu_info['threads'] = int(lines[1].strip())

            except Exception as e:
                cpu_info['error'] = str(e)

        return cpu_info

    def detect_memory(self) -> Dict[str, Any]:
        """Detect memory information."""
        mem_info = {
            'total_gb': 0,
            'available_gb': 0,
            'unit': 'GB'
        }

        if self.platform == 'Linux':
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            kb = int(line.split()[1])
                            mem_info['total_gb'] = round(kb / (1024**2), 1)
                        if 'MemAvailable' in line:
                            kb = int(line.split()[1])
                            mem_info['available_gb'] = round(kb / (1024**2), 1)
            except Exception as e:
                mem_info['error'] = str(e)

        elif self.platform == 'Darwin':
            try:
                result = subprocess.run(
                    ['sysctl', '-n', 'hw.memsize'],
                    capture_output=True, text=True, timeout=5
                )
                bytes_total = int(result.stdout.strip())
                mem_info['total_gb'] = round(bytes_total / (1024**3), 1)
            except Exception as e:
                mem_info['error'] = str(e)

        elif self.platform == 'Windows':
            try:
                result = subprocess.run(
                    ['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    bytes_total = int(lines[1].strip())
                    mem_info['total_gb'] = round(bytes_total / (1024**3), 1)
            except Exception as e:
                mem_info['error'] = str(e)

        return mem_info

    def detect_storage(self) -> Dict[str, Any]:
        """Detect storage information."""
        storage_info = {
            'total_gb': 0,
            'available_gb': 0,
            'filesystem': 'Unknown'
        }

        try:
            if self.platform == 'Windows':
                # For WSL, detect both WSL and Windows drives
                result = subprocess.run(
                    ['df', '-h', '/'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    storage_info['filesystem'] = parts[0]
                    # Parse size (e.g., "1.8T" -> 1800)
                    total_str = parts[1]
                    if 'T' in total_str:
                        storage_info['total_gb'] = int(float(total_str.replace('T', '')) * 1024)
                    elif 'G' in total_str:
                        storage_info['total_gb'] = int(float(total_str.replace('G', '')))
            else:
                result = subprocess.run(
                    ['df', '-h', '/'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    storage_info['filesystem'] = parts[0]
                    total_str = parts[1]
                    if 'T' in total_str:
                        storage_info['total_gb'] = int(float(total_str.replace('T', '')) * 1024)
                    elif 'G' in total_str:
                        storage_info['total_gb'] = int(float(total_str.replace('G', '')))

        except Exception as e:
            storage_info['error'] = str(e)

        return storage_info

    def detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU information."""
        gpu_info = {
            'model': 'Unknown',
            'vram_gb': 0,
            'available': False
        }

        try:
            if self.platform == 'Linux':
                # Try lspci first
                result = subprocess.run(
                    ['lspci'], capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'VGA' in line or 'Display' in line:
                        gpu_info['model'] = line.split(': ')[1] if ': ' in line else 'Integrated'
                        gpu_info['available'] = True
                        break

            elif self.platform == 'Windows':
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True, text=True, timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    gpu_info['model'] = lines[1].strip()
                    gpu_info['available'] = True

        except Exception:
            pass

        return gpu_info

    def detect_all(self) -> Dict[str, Any]:
        """Detect all machine specifications."""
        return {
            'machine_id': self.hostname,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'platform': {
                'os': self.platform,
                'os_version': platform.version(),
                'architecture': platform.machine()
            },
            'cpu': self.detect_cpu(),
            'memory': self.detect_memory(),
            'storage': self.detect_storage(),
            'gpu': self.detect_gpu()
        }

    def create_profile_classification(self, specs: Dict[str, Any]) -> str:
        """Classify machine profile based on specs."""
        mem_gb = specs['memory']['total_gb']
        cpu_threads = specs['cpu']['threads']

        if mem_gb >= 32 and cpu_threads >= 8:
            return 'high-performance'
        elif mem_gb >= 16 and cpu_threads >= 4:
            return 'standard'
        else:
            return 'low-power'

    def create_lug(self, save_path: Optional[Path] = None) -> Dict[str, Any]:
        """Create a machine profile lug."""
        specs = self.detect_all()
        classification = self.create_profile_classification(specs)

        lug = {
            'lug_type': 'machine-profile',
            'lug_version': '1.0.0',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'machine': {
                'id': self.hostname,
                'nickname': self.hostname,
                'classification': classification,
                'specs': specs
            },
            'recommended_settings': {
                'vscode': self._get_vscode_recommendations(classification, specs),
                'python': self._get_python_recommendations(classification, specs)
            }
        }

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(lug, f, indent=2)

        return lug

    def _get_vscode_recommendations(self, classification: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Get VSCode setting recommendations based on machine class."""
        if classification == 'high-performance':
            return {
                'python.analysis.typeCheckingMode': 'strict',
                'python.analysis.diagnosticMode': 'workspace',
                'python.analysis.memory.keepLibraryAst': True,
                'python.analysis.userFileIndexingLimit': 10000,
                'editor.bracketPairColorization.enabled': True,
                'editor.minimap.enabled': True,
                'editor.suggest.maxVisibleSuggestions': 15,
                'git.autorefresh': True,
                'git.autofetch': True
            }
        elif classification == 'standard':
            return {
                'python.analysis.typeCheckingMode': 'basic',
                'python.analysis.diagnosticMode': 'openFilesOnly',
                'python.analysis.memory.keepLibraryAst': False,
                'python.analysis.userFileIndexingLimit': 5000,
                'editor.bracketPairColorization.enabled': True,
                'editor.minimap.enabled': True,
                'git.autorefresh': False
            }
        else:
            return {
                'python.analysis.typeCheckingMode': 'off',
                'python.analysis.diagnosticMode': 'openFilesOnly',
                'python.analysis.memory.keepLibraryAst': False,
                'python.analysis.userFileIndexingLimit': 2000,
                'editor.bracketPairColorization.enabled': False,
                'editor.minimap.enabled': False,
                'git.autorefresh': False
            }

    def _get_python_recommendations(self, classification: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Get Python environment recommendations."""
        mem_gb = specs['memory']['total_gb']

        return {
            'max_workers': min(specs['cpu']['threads'], 8) if classification == 'high-performance' else 2,
            'cache_size_mb': int(mem_gb * 100) if classification == 'high-performance' else 512,
            'parallel_builds': classification == 'high-performance'
        }


def main():
    """CLI entry point."""
    import sys

    detector = MachineDetector()

    if '--json' in sys.argv:
        # Output raw JSON
        specs = detector.detect_all()
        print(json.dumps(specs, indent=2))
    elif '--save-to-hub' in sys.argv:
        # Save to hub
        hub_path = Path.cwd().parent / 'hub' / 'machines' / f'{detector.hostname}.lug.json'
        lug = detector.create_lug(save_path=hub_path)
        print(f"✓ Machine profile saved to {hub_path}")
        print(f"  Classification: {lug['machine']['classification']}")
        print(f"  CPU: {lug['machine']['specs']['cpu']['model']}")
        print(f"  RAM: {lug['machine']['specs']['memory']['total_gb']} GB")
    else:
        # Human-readable output
        specs = detector.detect_all()
        classification = detector.create_profile_classification(specs)

        print(f"\n🖥️  Machine Profile: {detector.hostname}")
        print(f"{'=' * 60}")
        print(f"Classification: {classification.upper()}")
        print(f"\nCPU:")
        print(f"  Model: {specs['cpu']['model']}")
        print(f"  Cores: {specs['cpu']['cores']}")
        print(f"  Threads: {specs['cpu']['threads']}")
        print(f"\nMemory:")
        print(f"  Total: {specs['memory']['total_gb']} GB")
        print(f"\nStorage:")
        print(f"  Total: {specs['storage']['total_gb']} GB")
        print(f"\nGPU:")
        print(f"  Model: {specs['gpu']['model']}")
        print(f"  Available: {specs['gpu']['available']}")
        print(f"\n💡 Run with --save-to-hub to save this profile")


if __name__ == '__main__':
    main()
