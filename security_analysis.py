#!/usr/bin/env python3
"""
🔒 InsideOut Platform Security & Code Quality Analysis
Comprehensive security vulnerability and code quality assessment
"""

import os
import re
import ast
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.vulnerabilities = []
        self.performance_issues = []
        self.structure_issues = []
        self.hallucinations = []
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run comprehensive analysis"""
        logger.info("🔍 Starting comprehensive security and quality analysis...")
        
        results = {
            "security_vulnerabilities": self.find_security_vulnerabilities(),
            "performance_issues": self.find_performance_issues(),
            "structure_issues": self.find_structure_issues(),
            "potential_hallucinations": self.find_hallucinations(),
            "dependency_vulnerabilities": self.check_dependencies(),
            "code_quality_metrics": self.calculate_code_metrics(),
            "docker_security": self.analyze_docker_security(),
            "database_security": self.analyze_database_security()
        }
        
        return results
    
    def find_security_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Find security vulnerabilities in code"""
        logger.info("🔒 Analyzing security vulnerabilities...")
        vulnerabilities = []
        
        # Security patterns to check
        security_patterns = {
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'cursor\.execute\s*\([^)]*\+[^)]*\)',
            ],
            "command_injection": [
                r'os\.system\s*\([^)]*\+[^)]*\)',
                r'subprocess\.(call|run|Popen)\s*\([^)]*\+[^)]*\)',
                r'shell=True',
            ],
            "insecure_random": [
                r'random\.random\(\)',
                r'random\.randint\(',
                r'random\.choice\(',
            ],
            "weak_crypto": [
                r'md5\(',
                r'sha1\(',
                r'DES\(',
                r'RC4\(',
            ]
        }
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for vuln_type, patterns in security_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            vulnerabilities.append({
                                "type": vuln_type,
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "code": match.group(),
                                "severity": self._get_severity(vuln_type),
                                "description": self._get_vuln_description(vuln_type)
                            })
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        return vulnerabilities
    
    def find_performance_issues(self) -> List[Dict[str, Any]]:
        """Find performance issues in code"""
        logger.info("⚡ Analyzing performance issues...")
        issues = []
        
        performance_patterns = {
            "inefficient_loops": [
                r'for\s+\w+\s+in\s+range\(len\(',
                r'while.*len\(',
            ],
            "string_concatenation": [
                r'\+\s*["\'][^"\']*["\']',
                r'["\'][^"\']*["\']\s*\+',
            ],
            "repeated_calculations": [
                r'len\([^)]+\)\s*[><=]',
                r'\.count\([^)]+\)\s*[><=]',
            ],
            "inefficient_data_structures": [
                r'list\(\)\.append',
                r'dict\(\)\.update',
            ]
        }
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for issue_type, patterns in performance_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append({
                                "type": issue_type,
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "code": match.group(),
                                "impact": self._get_performance_impact(issue_type),
                                "suggestion": self._get_performance_suggestion(issue_type)
                            })
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        return issues
    
    def find_structure_issues(self) -> List[Dict[str, Any]]:
        """Find structural and architectural issues"""
        logger.info("🏗️ Analyzing structural issues...")
        issues = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Analyze AST for structural issues
                analyzer = StructureAnalyzer()
                analyzer.visit(tree)
                
                for issue in analyzer.issues:
                    issue["file"] = str(py_file.relative_to(self.project_root))
                    issues.append(issue)
                    
            except Exception as e:
                logger.warning(f"Error parsing {py_file}: {e}")
        
        return issues
    
    def find_hallucinations(self) -> List[Dict[str, Any]]:
        """Find potential AI hallucinations or inconsistencies"""
        logger.info("🔍 Analyzing potential hallucinations...")
        hallucinations = []
        
        # Check for inconsistent imports
        import_patterns = {}
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                imports = re.findall(r'^(?:from\s+\S+\s+)?import\s+(.+)$', content, re.MULTILINE)
                for imp in imports:
                    if imp not in import_patterns:
                        import_patterns[imp] = []
                    import_patterns[imp].append(str(py_file.relative_to(self.project_root)))
            except Exception as e:
                logger.warning(f"Error analyzing imports in {py_file}: {e}")
        
        # Check for unused imports
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                # Find imports that are never used
                imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                for imp in imports:
                    if content.count(imp) == 1:  # Only appears in import line
                        hallucinations.append({
                            "type": "unused_import",
                            "file": str(py_file.relative_to(self.project_root)),
                            "import": imp,
                            "description": f"Import '{imp}' appears to be unused"
                        })
            except Exception as e:
                logger.warning(f"Error checking unused imports in {py_file}: {e}")
        
        return hallucinations
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check for vulnerable dependencies"""
        logger.info("📦 Analyzing dependencies...")
        
        results = {
            "requirements_files": [],
            "potential_vulnerabilities": [],
            "outdated_packages": []
        }
        
        # Find all requirements files
        req_files = list(self.project_root.rglob("requirements*.txt"))
        req_files.extend(list(self.project_root.rglob("pyproject.toml")))
        req_files.extend(list(self.project_root.rglob("Pipfile")))
        
        for req_file in req_files:
            results["requirements_files"].append(str(req_file.relative_to(self.project_root)))
            
            try:
                content = req_file.read_text(encoding='utf-8')
                # Check for known vulnerable packages
                vulnerable_packages = [
                    "pillow<8.3.2", "requests<2.25.1", "urllib3<1.26.5",
                    "pyyaml<5.4", "jinja2<2.11.3", "flask<1.1.4"
                ]
                
                for vuln_pkg in vulnerable_packages:
                    if vuln_pkg.split('<')[0] in content:
                        results["potential_vulnerabilities"].append({
                            "file": str(req_file.relative_to(self.project_root)),
                            "package": vuln_pkg,
                            "description": f"Potentially vulnerable version of {vuln_pkg.split('<')[0]}"
                        })
            except Exception as e:
                logger.warning(f"Error analyzing {req_file}: {e}")
        
        return results
    
    def calculate_code_metrics(self) -> Dict[str, Any]:
        """Calculate code quality metrics"""
        logger.info("📊 Calculating code metrics...")
        
        metrics = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "average_complexity": 0,
            "files_by_type": {}
        }
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                metrics["total_files"] += 1
                suffix = file_path.suffix
                if suffix not in metrics["files_by_type"]:
                    metrics["files_by_type"][suffix] = 0
                metrics["files_by_type"][suffix] += 1
                
                if suffix == ".py":
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        metrics["total_lines"] += len(content.splitlines())
                        
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                metrics["total_functions"] += 1
                            elif isinstance(node, ast.ClassDef):
                                metrics["total_classes"] += 1
                    except Exception as e:
                        logger.warning(f"Error analyzing {file_path}: {e}")
        
        return metrics
    
    def analyze_docker_security(self) -> List[Dict[str, Any]]:
        """Analyze Docker security issues"""
        logger.info("🐳 Analyzing Docker security...")
        issues = []
        
        docker_files = list(self.project_root.rglob("Dockerfile*"))
        docker_files.extend(list(self.project_root.rglob("docker-compose*.yml")))
        
        security_patterns = {
            "root_user": r'USER\s+root',
            "privileged_mode": r'privileged:\s*true',
            "host_network": r'network_mode:\s*host',
            "exposed_ports": r'ports:\s*-\s*["\']?\d+:\d+["\']?',
            "secrets_in_env": r'environment:.*password|secret|key',
        }
        
        for docker_file in docker_files:
            try:
                content = docker_file.read_text(encoding='utf-8')
                for issue_type, pattern in security_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            "type": issue_type,
                            "file": str(docker_file.relative_to(self.project_root)),
                            "line": line_num,
                            "code": match.group(),
                            "severity": "medium",
                            "description": f"Potential Docker security issue: {issue_type}"
                        })
            except Exception as e:
                logger.warning(f"Error analyzing {docker_file}: {e}")
        
        return issues
    
    def analyze_database_security(self) -> List[Dict[str, Any]]:
        """Analyze database security issues"""
        logger.info("🗄️ Analyzing database security...")
        issues = []
        
        sql_files = list(self.project_root.rglob("*.sql"))
        
        for sql_file in sql_files:
            try:
                content = sql_file.read_text(encoding='utf-8')
                
                # Check for common SQL security issues
                if re.search(r'CREATE\s+USER.*IDENTIFIED\s+BY\s+["\'][^"\']+["\']', content, re.IGNORECASE):
                    issues.append({
                        "type": "hardcoded_db_password",
                        "file": str(sql_file.relative_to(self.project_root)),
                        "severity": "high",
                        "description": "Hardcoded database password found in SQL file"
                    })
                
                if re.search(r'GRANT\s+ALL', content, re.IGNORECASE):
                    issues.append({
                        "type": "excessive_privileges",
                        "file": str(sql_file.relative_to(self.project_root)),
                        "severity": "medium",
                        "description": "Excessive database privileges granted"
                    })
                    
            except Exception as e:
                logger.warning(f"Error analyzing {sql_file}: {e}")
        
        return issues
    
    def _get_severity(self, vuln_type: str) -> str:
        severity_map = {
            "hardcoded_secrets": "high",
            "sql_injection": "critical",
            "command_injection": "critical",
            "insecure_random": "medium",
            "weak_crypto": "high"
        }
        return severity_map.get(vuln_type, "medium")
    
    def _get_vuln_description(self, vuln_type: str) -> str:
        descriptions = {
            "hardcoded_secrets": "Hardcoded secrets can be exposed in version control",
            "sql_injection": "SQL injection vulnerability detected",
            "command_injection": "Command injection vulnerability detected",
            "insecure_random": "Using insecure random number generation",
            "weak_crypto": "Using weak cryptographic algorithm"
        }
        return descriptions.get(vuln_type, "Security vulnerability detected")
    
    def _get_performance_impact(self, issue_type: str) -> str:
        impact_map = {
            "inefficient_loops": "high",
            "string_concatenation": "medium",
            "repeated_calculations": "medium",
            "inefficient_data_structures": "low"
        }
        return impact_map.get(issue_type, "low")
    
    def _get_performance_suggestion(self, issue_type: str) -> str:
        suggestions = {
            "inefficient_loops": "Use enumerate() or direct iteration instead of range(len())",
            "string_concatenation": "Use f-strings or join() for string concatenation",
            "repeated_calculations": "Cache calculation results in variables",
            "inefficient_data_structures": "Initialize data structures with proper size"
        }
        return suggestions.get(issue_type, "Consider optimizing this code")

class StructureAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.function_complexity = {}
        self.class_methods = {}
    
    def visit_FunctionDef(self, node):
        # Check function complexity
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            self.issues.append({
                "type": "high_complexity",
                "line": node.lineno,
                "function": node.name,
                "complexity": complexity,
                "description": f"Function '{node.name}' has high cyclomatic complexity ({complexity})"
            })
        
        # Check function length
        if len(node.body) > 50:
            self.issues.append({
                "type": "long_function",
                "line": node.lineno,
                "function": node.name,
                "lines": len(node.body),
                "description": f"Function '{node.name}' is too long ({len(node.body)} statements)"
            })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        # Check class size
        if len(node.body) > 20:
            self.issues.append({
                "type": "large_class",
                "line": node.lineno,
                "class": node.name,
                "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                "description": f"Class '{node.name}' is too large"
            })
        
        self.generic_visit(node)
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

def generate_report(results: Dict[str, Any]) -> str:
    """Generate comprehensive security report"""
    report = []
    report.append("=" * 80)
    report.append("🔒 INSIDEOUT PLATFORM SECURITY & QUALITY ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Security Vulnerabilities
    vulns = results["security_vulnerabilities"]
    report.append(f"🚨 SECURITY VULNERABILITIES: {len(vulns)} found")
    report.append("-" * 50)
    
    severity_counts = {}
    for vuln in vulns:
        severity = vuln["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        report.append(f"  [{vuln['severity'].upper()}] {vuln['type']} in {vuln['file']}:{vuln['line']}")
        report.append(f"    Code: {vuln['code']}")
        report.append(f"    Description: {vuln['description']}")
        report.append("")
    
    report.append(f"Severity breakdown: {severity_counts}")
    report.append("")
    
    # Performance Issues
    perf_issues = results["performance_issues"]
    report.append(f"⚡ PERFORMANCE ISSUES: {len(perf_issues)} found")
    report.append("-" * 50)
    
    for issue in perf_issues[:10]:  # Show top 10
        report.append(f"  [{issue['impact'].upper()}] {issue['type']} in {issue['file']}:{issue['line']}")
        report.append(f"    Suggestion: {issue['suggestion']}")
        report.append("")
    
    # Structure Issues
    struct_issues = results["structure_issues"]
    report.append(f"🏗️ STRUCTURAL ISSUES: {len(struct_issues)} found")
    report.append("-" * 50)
    
    for issue in struct_issues[:10]:  # Show top 10
        report.append(f"  {issue['type']} in {issue['file']}:{issue['line']}")
        report.append(f"    Description: {issue['description']}")
        report.append("")
    
    # Code Quality Metrics
    metrics = results["code_quality_metrics"]
    report.append("📊 CODE QUALITY METRICS")
    report.append("-" * 50)
    report.append(f"  Total files: {metrics['total_files']}")
    report.append(f"  Total lines: {metrics['total_lines']}")
    report.append(f"  Total functions: {metrics['total_functions']}")
    report.append(f"  Total classes: {metrics['total_classes']}")
    report.append(f"  Files by type: {metrics['files_by_type']}")
    report.append("")
    
    # Docker Security
    docker_issues = results["docker_security"]
    report.append(f"🐳 DOCKER SECURITY ISSUES: {len(docker_issues)} found")
    report.append("-" * 50)
    
    for issue in docker_issues:
        report.append(f"  [{issue['severity'].upper()}] {issue['type']} in {issue['file']}:{issue['line']}")
        report.append(f"    Description: {issue['description']}")
        report.append("")
    
    # Summary
    report.append("=" * 80)
    report.append("📋 SUMMARY")
    report.append("=" * 80)
    
    total_critical = len([v for v in vulns if v["severity"] == "critical"])
    total_high = len([v for v in vulns if v["severity"] == "high"])
    total_medium = len([v for v in vulns if v["severity"] == "medium"])
    
    if total_critical > 0:
        report.append(f"❌ CRITICAL: {total_critical} critical security vulnerabilities found!")
        report.append("   Immediate action required before production deployment.")
    elif total_high > 0:
        report.append(f"⚠️  HIGH RISK: {total_high} high-severity issues found.")
        report.append("   Address these issues before production deployment.")
    elif total_medium > 0:
        report.append(f"⚠️  MEDIUM RISK: {total_medium} medium-severity issues found.")
        report.append("   Consider addressing these issues for better security.")
    else:
        report.append("✅ GOOD: No critical security vulnerabilities found!")
    
    report.append("")
    report.append(f"Performance issues: {len(perf_issues)}")
    report.append(f"Structural issues: {len(struct_issues)}")
    report.append(f"Docker security issues: {len(docker_issues)}")
    
    return "\n".join(report)

def main():
    """Main analysis function"""
    project_root = "/workspace/project/SentinentalBERT"
    
    print("🔍 Starting InsideOut Platform Security Analysis...")
    print("=" * 80)
    
    analyzer = SecurityAnalyzer(project_root)
    results = analyzer.analyze_all()
    
    # Generate and save report
    report = generate_report(results)
    
    # Save detailed results as JSON
    with open(f"{project_root}/security_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save human-readable report
    with open(f"{project_root}/security_analysis_report.txt", "w") as f:
        f.write(report)
    
    print(report)
    print("\n" + "=" * 80)
    print("📄 Detailed results saved to:")
    print(f"  - security_analysis_results.json")
    print(f"  - security_analysis_report.txt")
    print("=" * 80)

if __name__ == "__main__":
    main()