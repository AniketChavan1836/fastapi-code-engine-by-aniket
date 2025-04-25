import subprocess, uuid, os

# Common runner invoking nsjail
def _run_sandbox(cmd, sandbox_dir, timeout=5, mem_mb=64):
    base = os.getcwd()
    nsjail_cmd = [
        'nsjail',
        '--quiet',              # suppress nsjail logs
        '--chroot', sandbox_dir,
        '--disable_proc',
        '--disable_raw_syscalls',
        '--disable_clone_newnet',  # no network
        '--max_cpus', '1',
        '--cgroup_mem_max', str(mem_mb * 1024 * 1024),
        '--time_limit', str(timeout),
        '--rlimit_as', str(mem_mb * 1024 * 1024),
        '--rlimit_cpu', str(timeout),
        '--workdir', '/sandbox',
        '--',
    ] + cmd
    try:
        result = subprocess.run(
            nsjail_cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 1
        )
        return {'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired:
        return {'error': 'Execution timed out.'}

# Execute Python code
def execute_python(code: str) -> dict:
    sandbox_dir = 'sandbox'
    os.makedirs(sandbox_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}.py"
    path = os.path.join(sandbox_dir, fname)
    with open(path, 'w') as f:
        f.write(code)
    return _run_sandbox(['python3', fname], sandbox_dir)

# Execute C++ code
def execute_cpp(code: str) -> dict:
    sandbox_dir = 'sandbox'
    os.makedirs(sandbox_dir, exist_ok=True)
    cpp = f"{uuid.uuid4().hex}.cpp"
    exe = cpp.replace('.cpp', '')
    cpp_path = os.path.join(sandbox_dir, cpp)
    with open(cpp_path, 'w') as f:
        f.write(code)
    # Compile
    comp = subprocess.run(
        ['g++', cpp, '-O2', '-std=c++17', '-o', exe],
        cwd=sandbox_dir,
        capture_output=True,
        text=True
    )
    if comp.returncode != 0:
        return {'compile_error': comp.stderr}
    return _run_sandbox([f'./{exe}'], sandbox_dir)

# Execute Java code
def execute_java(code: str) -> dict:
    sandbox_dir = 'sandbox'
    os.makedirs(sandbox_dir, exist_ok=True)
    class_name = 'Main'
    java_file = f"{class_name}.java"
    java_path = os.path.join(sandbox_dir, java_file)
    with open(java_path, 'w') as f:
        f.write(code)
    # Compile
    comp = subprocess.run(
        ['javac', java_file],
        cwd=sandbox_dir,
        capture_output=True,
        text=True
    )
    if comp.returncode != 0:
        return {'compile_error': comp.stderr}
    return _run_sandbox(['java', class_name], sandbox_dir)
