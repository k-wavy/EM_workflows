#!/usr/bin/env python3

import sys
import os
import subprocess

def run_step(feabas_path, script_name, mode):
    script_path = os.path.join(feabas_path, "scripts", script_name)
    print(f"{script_name.replace('_main.py', '')} {mode}")
    cmd = ["python", script_path, "--mode", mode]
    
    # Using check=True to stop execution if a step fails, mirroring bash '&&'
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 2:
        print("please give location of feabas")
        sys.exit(1)

    feabas = sys.argv[1]

    steps = [
        ("stitch_main.py", "matching"),
        ("stitch_main.py", "optimization"),
        ("stitch_main.py", "rendering"),
        ("thumbnail_main.py", "downsample"),
        ("thumbnail_main.py", "match"),
        ("thumbnail_main.py", "optimization"),
        ("thumbnail_main.py", "render"),
        ("align_main.py", "meshing"),
        ("align_main.py", "matching"),
        ("align_main.py", "optimization"),
        ("align_main.py", "rendering"),
        ("align_main.py", "downsample")
    ]

    for script, mode in steps:
        try:
            run_step(feabas, script, mode)
        except subprocess.CalledProcessError as e:
            print(f"Step failed: {script} --mode {mode}")
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()