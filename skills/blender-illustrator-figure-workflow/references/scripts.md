# 脚本使用与边界

## render_preserving_scene.py

在独立后台 Blender 进程中使用，避免替换用户正在编辑的场景。脚本读取已有 `.blend`，不写回源文件；配置中的相对路径以 JSON 所在目录为基准。复制 [示例清单](render-manifest.example.json) 到项目目录，填写真实源文件和新输出路径。

```powershell
& 'C:\Program Files\Blender Foundation\Blender\blender.exe' --background --disable-autoexec --python-exit-code 1 --python 'path/to/render_preserving_scene.py' -- 'path/to/render-manifest.json' --cpu
```

Blender 路径是示例，按实际安装路径替换。可先用普通 Python 检查清单：

```text
python render_preserving_scene.py render-manifest.json --validate-only
```

`--cpu` 只覆盖 Cycles 设备；省略则继承场景设置。`samples` 可省略以继承已有质量；清单也可指定 `scene`，否则使用文件中当前场景。输出是 8-bit RGBA PNG，继承 film_transparent、环境、材质与色彩管理；不同输出位深应按项目要求扩展。

每个渲染有独立 `.render.json` 报告。已有 PNG 或报告不会覆盖。批次中途失败时，已完成的文件保留；检查后为未完成作业建立新清单，而非覆盖重跑。脚本拒绝启用渲染边界的场景和可检测到的活动合成器 File Output 节点；复杂或新版合成器需先在应用内检查其他输出副作用。

快照覆盖相机、显式灯光、透明背景和主要色彩设置；它不是完整材质节点或合成器审计。脚本不修改这些节点，但驱动器、外部依赖、动画、渲染处理器和版本差异仍需在实际图像中核验。只处理可信项目文件，并保持 `--disable-autoexec`。

## inspect_illustrator.jsx

在 Illustrator 的“文件 → 脚本 → 其他脚本”中运行。选择目标打开文档的序号，再选择新的 `.txt` 报告路径。脚本不保存、不改动、不切换文档内容；仅输出图层、对象、几何边界、文本和可用 UUID/矩阵。

报告可能含私有图中文字和本机路径，应作为项目内调试数据。它不是可直接重复执行的修改清单。对实际替换、裁切和删除，应根据本次检查生成范围明确的脚本，并遵循 [原位编辑说明](illustrator-in-place.md)。
