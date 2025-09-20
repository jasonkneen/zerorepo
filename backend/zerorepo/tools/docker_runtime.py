"""
Docker runtime for isolated test execution and code validation.
"""

import docker
import os
import shlex
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DockerTestRunner:
    """
    Docker-based test runner for isolated code execution.
    
    Provides sandboxed environment for running pytest and validating generated code.
    """
    
    def __init__(self, base_image: str = "python:3.11-slim"):
        self.base_image = base_image
        self.client = None
        self._setup_docker_client()
        
    def _setup_docker_client(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            logger.info(f"Docker client initialized with base image: {self.base_image}")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            # For development/testing, we'll use subprocess fallback
            self.client = None
            
    async def run_tests(self, test_file_path: str, timeout: int = 30) -> Dict:
        """
        Run tests for a specific test file.
        
        Args:
            test_file_path: Path to test file
            timeout: Execution timeout in seconds
            
        Returns:
            Test execution result dict
        """
        if not os.path.exists(test_file_path):
            return {
                "success": False,
                "error": f"Test file not found: {test_file_path}",
                "output": ""
            }
            
        # If Docker is not available, use subprocess fallback
        if self.client is None:
            return await self._run_tests_subprocess(test_file_path, timeout)
            
        return await self._run_tests_docker(test_file_path, timeout)
        
    async def run_all_tests(self, project_dir: str, timeout: int = 120) -> Dict:
        """
        Run all tests in a project directory.
        
        Args:
            project_dir: Project root directory
            timeout: Execution timeout in seconds
            
        Returns:
            Aggregated test results
        """
        test_dir = os.path.join(project_dir, "tests")
        
        if not os.path.exists(test_dir):
            return {
                "success": False,
                "error": "No tests directory found",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0
            }
            
        # If Docker is not available, use subprocess fallback
        if self.client is None:
            return await self._run_all_tests_subprocess(project_dir, timeout)
            
        return await self._run_all_tests_docker(project_dir, timeout)
        
    async def _run_tests_docker(self, test_file_path: str, timeout: int) -> Dict:
        """Run tests using Docker container."""
        
        try:
            project_dir = self._get_project_root(test_file_path)
            rel_test_path = os.path.relpath(test_file_path, project_dir)

            # Create temporary directory for test execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy full project into isolated workspace
                self._prepare_project_environment(project_dir, temp_dir)

                requirements_file = os.path.join(project_dir, "requirements.txt")
                install_steps: List[str] = []
                if os.path.exists(requirements_file):
                    install_steps.append("pip install -r requirements.txt")
                install_steps.append("pip install pytest")

                pytest_command = f"python -m pytest {shlex.quote(rel_test_path)} -v --tb=short"
                command_steps = install_steps + [pytest_command]
                command = "bash -c \"{}\"".format(" && ".join(command_steps))

                # Create container
                container = self.client.containers.run(
                    self.base_image,
                    command=command,
                    volumes={temp_dir: {'bind': '/project', 'mode': 'rw'}},
                    working_dir='/project',
                    detach=True,
                    remove=True,
                    network_mode='none',  # No network access
                    mem_limit='512m',     # Memory limit
                    cpu_count=1
                )
                
                # Wait for completion with timeout
                try:
                    result = container.wait(timeout=timeout)
                    output = container.logs().decode('utf-8')
                    
                    return {
                        "success": result['StatusCode'] == 0,
                        "output": output,
                        "exit_code": result['StatusCode'],
                        "error": "" if result['StatusCode'] == 0 else "Tests failed"
                    }
                    
                except docker.errors.ContainerError as e:
                    return {
                        "success": False,
                        "output": str(e),
                        "error": "Container execution error"
                    }
                    
        except Exception as e:
            logger.error(f"Docker test execution error: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": f"Docker execution failed: {str(e)}"
            }
            
    async def _run_tests_subprocess(self, test_file_path: str, timeout: int) -> Dict:
        """Fallback: run tests using subprocess."""
        
        try:
            import subprocess

            project_dir = self._get_project_root(test_file_path)
            rel_test_path = os.path.relpath(test_file_path, project_dir)

            cmd = ["python", "-m", "pytest", rel_test_path, "-v", "--tb=short"]

            # Run with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=project_dir
            )
            
            try:
                stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
                output = stdout.decode('utf-8') if stdout else ""
                
                return {
                    "success": process.returncode == 0,
                    "output": output,
                    "exit_code": process.returncode,
                    "error": "" if process.returncode == 0 else "Tests failed"
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Test execution timed out after {timeout}s"
                }
                
        except Exception as e:
            logger.error(f"Subprocess test execution error: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": f"Test execution failed: {str(e)}"
            }
            
    async def _run_all_tests_docker(self, project_dir: str, timeout: int) -> Dict:
        """Run all tests using Docker."""
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy entire project for testing
                self._prepare_project_environment(project_dir, temp_dir)
                
                # Install dependencies first
                requirements_file = os.path.join(project_dir, "requirements.txt")
                install_steps: List[str] = []
                if os.path.exists(requirements_file):
                    install_steps.append("pip install -r requirements.txt")
                install_steps.append("pip install pytest")

                integration_command = (
                    "python -m pytest tests/ -v --tb=short --json-report --json-report-file=test_results.json"
                )
                command_steps = install_steps + [integration_command]
                command = "bash -c \"{}\"".format(" && ".join(command_steps))

                container = self.client.containers.run(
                    self.base_image,
                    command=command,
                    volumes={temp_dir: {'bind': '/project', 'mode': 'rw'}},
                    working_dir='/project',
                    detach=True,
                    remove=True,
                    network_mode='none',
                    mem_limit='1g',
                    cpu_count=2
                )
                
                try:
                    result = container.wait(timeout=timeout)
                    output = container.logs().decode('utf-8')
                    
                    # Parse test results if available
                    test_stats = self._parse_test_output(output)
                    
                    return {
                        "success": result['StatusCode'] == 0,
                        "output": output,
                        "exit_code": result['StatusCode'],
                        **test_stats
                    }
                    
                except docker.errors.ContainerError as e:
                    return {
                        "success": False,
                        "output": str(e),
                        "total_tests": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "error": "Container execution error"
                    }
                    
        except Exception as e:
            logger.error(f"Docker integration test error: {str(e)}")
            return {
                "success": False,
                "output": "",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error": f"Docker execution failed: {str(e)}"
            }
            
    async def _run_all_tests_subprocess(self, project_dir: str, timeout: int) -> Dict:
        """Fallback: run all tests using subprocess."""
        
        try:
            import subprocess
            
            cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=project_dir
            )
            
            try:
                stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
                output = stdout.decode('utf-8') if stdout else ""
                
                test_stats = self._parse_test_output(output)
                
                return {
                    "success": process.returncode == 0,
                    "output": output,
                    "exit_code": process.returncode,
                    **test_stats
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "output": "",
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "error": f"Integration test timed out after {timeout}s"
                }
                
        except Exception as e:
            logger.error(f"Subprocess integration test error: {str(e)}")
            return {
                "success": False,
                "output": "",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error": f"Integration test failed: {str(e)}"
            }
            
    def _get_project_root(self, test_file_path: str) -> str:
        """Infer project root directory from a test file path."""

        test_path = Path(test_file_path).resolve()

        for parent in test_path.parents:
            if parent.name == "tests":
                return str(parent.parent)

        return str(test_path.parent)

    def _prepare_project_environment(self, project_dir: str, temp_dir: str) -> None:
        """Prepare project environment for integration testing."""
        
        import shutil
        
        # Copy project files (excluding .git, __pycache__, etc.)
        exclude_patterns = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.env'}
        
        for item in os.listdir(project_dir):
            if item not in exclude_patterns:
                src_path = os.path.join(project_dir, item)
                dst_path = os.path.join(temp_dir, item)
                
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, ignore=shutil.ignore_patterns(*exclude_patterns))
                else:
                    shutil.copy2(src_path, dst_path)
                    
    def _parse_test_output(self, output: str) -> Dict:
        """Parse pytest output to extract test statistics."""
        
        stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # Look for pytest summary line
            if " passed" in line or " failed" in line:
                # Parse patterns like "5 passed, 2 failed"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        try:
                            stats["passed_tests"] = int(parts[i-1])
                        except ValueError:
                            pass
                    elif part == "failed" and i > 0:
                        try:
                            stats["failed_tests"] = int(parts[i-1])
                        except ValueError:
                            pass
                            
        stats["total_tests"] = stats["passed_tests"] + stats["failed_tests"]
        
        return stats
        
    def cleanup(self):
        """Cleanup Docker resources."""
        if self.client:
            try:
                # Remove any dangling containers
                containers = self.client.containers.list(all=True, filters={"status": "exited"})
                for container in containers:
                    container.remove()
                    
                logger.info("Docker cleanup completed")
            except Exception as e:
                logger.warning(f"Docker cleanup error: {str(e)}")
