import os
import subprocess
import sys
from pathlib import Path
import pkg_resources

def get_installed_packages():
    """获取已安装的包及其版本"""
    return [(dist.key, dist.version) for dist in pkg_resources.working_set]

def analyze_environment():
    """分析构建环境"""
    print("=== Environment Analysis ===")
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print(f"Virtual Env: {os.environ.get('VIRTUAL_ENV', 'Not in a virtual environment')}")
    print("\nInstalled Packages:")
    for package, version in get_installed_packages():
        print(f"  - {package} ({version})")
    print("="*30)

def build():
    analyze_environment()
    
    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        print("Warning: Not running in a virtual environment!")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() != 'y':
            return 1
    
    python_path = str(Path(venv_path) / "Scripts" / "python.exe") if venv_path else sys.executable
    site_packages = str(Path(venv_path) / "Lib" / "site-packages") if venv_path else ""
    
    cmd = [
        python_path,
        "-m", "nuitka",
        "--standalone",
        "--enable-plugin=pyside6",
        "--windows-console-mode=attach",
        "--windows-icon-from-ico=swan_icon.png",
        "--onefile-windows-splash-screen-image=swan_icon.png",
        "--nofollow-imports",
        "--follow-import-to=src",
        "--remove-output",
        "--show-progress",
        "--show-modules",
        "--output-filename=Swan",
        "--include-data-files=swan.config.toml=swan.config.toml",
        "--include-data-dir=env/Lib/site-packages/pyqttoast/css=pyqttoast/css",
        "--include-data-dir=env/Lib/site-packages/pyqttoast/icons=pyqttoast/icons",
        "./main.py"
    ]
    
    env = os.environ.copy()
    if site_packages:
        env["PYTHONPATH"] = site_packages
    
    print("\n=== Build Configuration ===")
    print(f"Python interpreter: {python_path}")
    print(f"Site-packages: {site_packages}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Command: {' '.join(cmd)}")
    print("="*30 + "\n")
    
    dist_dir = 'main.dist'
    
    exclude_lib_file = [
        'swan.config.toml'
    ]
    
    result = subprocess.run(
        cmd,
        env=env
    )
    
    # 输出构建日志
    # log_file = "build_log.txt"
    # with open(log_file, "w", encoding="utf-8") as f:
    #     f.write("=== STDOUT ===\n")
    #     f.write(result.stdout)
    #     f.write("\n=== STDERR ===\n")
    #     f.write(result.stderr)
    
    # print(f"\nBuild log saved to: {log_file}")
    
    if result.returncode != 0:
        print("\nBuild failed! Check the log file for details.")
    else:
        print("\nBuild completed successfully!")
        
        # 检查输出文件大小
        output_path = Path(dist_dir)
        if output_path.exists():
            total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
            print(f"\nOutput size: {total_size / (1024*1024):.2f} MB")
    
        # 移动相关文件
        if os.path.exists(dist_dir):
            lib_dir = Path(dist_dir).joinpath('lib')
            os.makedirs(lib_dir, exist_ok=True)
            
    return result.returncode

if __name__ == "__main__":
    try:
        exit_code = build()
        print(f"\nBuild finished with exit code: {exit_code}")
    except Exception as e:
        print(f"Build failed with error: {e}")
        exit(1)