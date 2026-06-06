# 环境笔记

这个项目在 Windows + WSL Ubuntu 上调试。

## 硬件

- NVIDIA RTX 4070 Laptop GPU / 4070 Ti 级别
- 显存约 8GB
- Windows + WSL Ubuntu

## Conda 环境

建议分开维护环境：

```text
inpaint360gs  -> Inpaint360GS / segmentation / render
lama4070      -> LaMa GPU color/depth inpainting
dreamgaussian -> DreamGaussian text/image-to-3D
```

不要把 LaMa、DreamGaussian、Inpaint360GS 全部依赖装进同一个环境。调试过程中最容易出问题的是 PyTorch、NumPy、SciPy、CUDA 扩展和 Hugging Face 依赖互相覆盖。

## 常见坑

### PyTorch / NumPy ABI 错误

如果遇到：

```text
expected np.ndarray (got numpy.ndarray)
```

可能是 PyTorch 和 NumPy ABI 不匹配。可以把图像读取函数改成不经过 `torch.from_numpy(np.array(...))`。

### SciPy / NumPy 错误

如果遇到：

```text
ValueError: All ufuncs must have type numpy.ufunc
```

可以固定：

```bash
pip install --force-reinstall "numpy==1.26.4" "scipy==1.11.4"
```

### DreamGaussian 扩展

`simple-knn` 和 `diff-gaussian-rasterization` 需要能找到 `nvcc` 和 PyTorch 动态库。必要时设置：

```bash
export CUDA_HOME=$CONDA_PREFIX
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:$CONDA_PREFIX/targets/x86_64-linux/lib:$LD_LIBRARY_PATH
```

### 大模型缓存

如果 C 盘空间不足，建议把 Hugging Face / torch / pip cache 指到 D 盘：

```bash
export HF_HOME=/mnt/d/ai_cache/huggingface
export HUGGINGFACE_HUB_CACHE=/mnt/d/ai_cache/huggingface/hub
export TORCH_HOME=/mnt/d/ai_cache/torch
export PIP_CACHE_DIR=/mnt/d/ai_cache/pip
```

