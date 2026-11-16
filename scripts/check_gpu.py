"""Check that PyTorch can use the RTX 5080 (Blackwell, sm_120).

Usage: uv run python scripts/check_gpu.py
Exits with code 1 if any check fails.
"""

import sys
import time

import torch


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def main() -> None:
    print(f"torch {torch.__version__} | CUDA build {torch.version.cuda}")

    # 1. Does torch see a GPU at all?
    if not torch.cuda.is_available():
        fail("torch.cuda.is_available() is False (CPU-only wheel or driver problem).")
    device = torch.device("cuda")
    print(f"[OK] GPU: {torch.cuda.get_device_name(device)}")

    # 2. Compute capability of the card (Blackwell consumer = 12.0)
    major, minor = torch.cuda.get_device_capability(device)
    print(f"[OK] Compute capability: sm_{major}{minor}")

    # 3. Was this torch build compiled for that architecture?
    arch = f"sm_{major}{minor}"
    if arch not in torch.cuda.get_arch_list():
        fail(f"{arch} not in compiled archs {torch.cuda.get_arch_list()}. Use cu128+ wheels.")
    print(f"[OK] {arch} is in the compiled archs")

    # 4. Real work: matrix multiplication on GPU vs CPU
    n = 4096
    a = torch.randn(n, n)
    b = torch.randn(n, n)

    start = time.perf_counter()
    c_cpu = a @ b
    cpu_ms = (time.perf_counter() - start) * 1000

    a_gpu, b_gpu = a.to(device), b.to(device)
    _ = a_gpu @ b_gpu  # warm-up: the first call initialises CUDA kernels
    torch.cuda.synchronize()
    start = time.perf_counter()
    c_gpu = a_gpu @ b_gpu
    torch.cuda.synchronize()  # GPU runs asynchronously: wait before stopping the clock
    gpu_ms = (time.perf_counter() - start) * 1000

    # GPU may use TF32 / different summation order, so compare with a tolerance
    if not torch.allclose(c_cpu, c_gpu.cpu(), rtol=1e-2, atol=1e-1):
        fail("GPU and CPU results differ.")
    print(f"[OK] matmul {n}x{n}: CPU {cpu_ms:.1f} ms | GPU {gpu_ms:.1f} ms | results match")

    free, total = torch.cuda.mem_get_info(device)
    print(f"[OK] VRAM: {free / 1e9:.1f} GB free of {total / 1e9:.1f} GB")
    print("All checks passed.")


if __name__ == "__main__":
    main()
