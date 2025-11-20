#!/usr/bin/env python3
"""
PyTorch 版本与 GPU 架构兼容性速查表
"""

compatibility = {
    "PyTorch 1.10.0": {
        "supported": "sm_37, sm_50, sm_60, sm_70, sm_75, sm_80, sm_86",
        "max_arch": "Ampere (RTX 3090, A100)",
        "rtx_4090": "❌ 不支持 (sm_89)",
        "h20": "❌ 不支持 (sm_90)"
    },
    "PyTorch 1.13.0": {
        "supported": "sm_37, sm_50, sm_60, sm_70, sm_75, sm_80, sm_86, sm_89",
        "max_arch": "Ada Lovelace (RTX 4090)",
        "rtx_4090": "✅ 支持 (sm_89)",
        "h20": "❌ 不支持 (sm_90)"
    },
    "PyTorch 2.0.1": {
        "supported": "sm_50, sm_60, sm_70, sm_75, sm_80, sm_86, sm_89, sm_90",
        "max_arch": "Hopper (H100, H20)",
        "rtx_4090": "✅ 支持 (sm_89)",
        "h20": "✅ 支持 (sm_90)"
    },
    "PyTorch 2.1.0+": {
        "supported": "sm_50, sm_60, sm_70, sm_75, sm_80, sm_86, sm_89, sm_90",
        "max_arch": "Hopper (H100, H20)",
        "rtx_4090": "✅ 支持 (sm_89)",
        "h20": "✅ 支持 (sm_90)"
    },
}

print("="*80)
print("GPU 架构与 PyTorch 版本兼容性")
print("="*80)

for version, info in compatibility.items():
    print(f"\n{version}:")
    for key, value in info.items():
        print(f"  {key}: {value}")

print("\n" + "="*80)
print("推荐方案")
print("="*80)

print("""
【本地 RTX 4090 可用】:
  - PyTorch 1.13.0 + CUDA 11.6 ✅ (最稳定，已验证能工作)
  - PyTorch 2.0.1 + CUDA 11.8 ✅
  - PyTorch 2.1.0 + CUDA 12.1 ⚠️  (可能有兼容性问题)

【服务器 H20 必须】:
  - PyTorch 2.0.1 + CUDA 11.8 ✅ (推荐 - 最老的支持 sm_90 版本)
  - PyTorch 2.1.0 + CUDA 12.1 ⚠️  (较新，可能不稳定)
  - PyTorch 2.4.1 + CUDA 12.1 ❌ (已验证会 segfault)

【结论】:
  服务器 (H20) 应该使用: PyTorch 2.0.1 + CUDA 11.8
  这是支持 sm_90 的最保守选择，与 Isaac Gym 兼容性最好
""")

print("="*80)
