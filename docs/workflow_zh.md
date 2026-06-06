# EditAnythingGS 流程说明

这个项目的目标是把 Inpaint360GS 的物体移除/补全能力和 DreamGaussian 的物体生成能力接起来，做成一个能展示的 3DGS 编辑项目。

## 总流程

```text
真实图像序列
  -> COLMAP / 3DGS 重建
  -> SAM2 目标 mask
  -> mask 转换为 Inpaint360GS 可读格式
  -> object distillation
  -> 物体移除
  -> 虚拟视角生成
  -> Segment-and-Track-Anything 传播 mask
  -> LaMa color/depth inpainting
  -> fused PLY
  -> Inpaint360GS 3D 补全
  -> DreamGaussian 生成新物体 PLY
  -> 合并新物体 PLY 到编辑后的场景
  -> RGB-only render 预览
```

## 为什么不用 CropFormer

原论文使用 CropFormer 生成 entity masks。我的设备显存约 8GB，在自定义数据集上 CropFormer 容易出现 OOM，而且分割质量不稳定。因此我使用手动 prompt 的 SAM2 mask 作为替代。这样牺牲了一部分自动化，但提升了可控性，也更适合练习项目。

## 关键脚本

`convert_sam2_masks.py`  
把已有 SAM2 mask 转成 Inpaint360GS 的 `raw_*`、`associated_*`、`associated_*_color` 和 `scene.json`。

`render_rgb_model.py`  
只渲染 RGB，不加载语义 classifier。用于预览外部合并进来的 DreamGaussian 物体，避免类别数不匹配。

`insert_dreamgaussian_object.py`  
把 DreamGaussian 生成的 `point_cloud.ply` 经过 scale / translation / rotation 后合并到 Inpaint360GS 场景 PLY。

`insert_dreamgaussian_at_object.py`  
尝试根据语义 classifier 找到目标物体 bbox，并把新物体自动放到目标位置。实际使用时要注意语义点云可能有离群点，必要时改用手动 `tx/ty/tz`。

`create_fused_mask_ply.py`  
把 LaMa 补全后的虚拟视角 color/depth 融合成 Inpaint360GS 后续补全需要的 masked PLY。

## 当前项目结果

当前已完成：

- 自定义数据集 `video2_table` 的 3DGS 重建
- SAM2 mask 替代 CropFormer
- 水瓶目标的 3DGS 物体移除
- LaMa GPU 环境下的 color/depth inpainting
- Inpaint360GS 3D 补全
- DreamGaussian 小汽车生成
- 小汽车 PLY 合并到 Inpaint360GS 场景并渲染预览

## 后续可以改进

1. 用深度/平面拟合自动估计桌面高度。
2. 让用户在某一帧点击插入点，再反投影到 3D。
3. 对 DreamGaussian 物体做尺度归一化和朝向规范化。
4. 给新插入物体重新训练语义 classifier，使它也能被后续编辑。
5. 使用更强的 image-to-3D 模型替代 DreamGaussian，提升物体质量。

