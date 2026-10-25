# Blender + Illustrator Figure Workflow

**作者 / Author：gaijichuan**  
**Skill 名称：`blender-illustrator-figure-workflow`**

将科研图的参考拆解、三维建模、高清渲染、Illustrator 原位更新和最终裁切组织成可重复使用的工作流。特别适合在用户多轮修改过的可编辑总图中，继续替换模型并保留现有布局。

## 包含内容

- 连续纤维包覆、融合节点和穿模颗粒的判定方法。
- 继承原相机、材质、环境光和景深的批量渲染脚本。
- Illustrator 当前文档的只读结构检查脚本。
- 模型原位替换、文本/下标修改、对齐与背景裁切操作指南。
- 渲染清单示例、验收检查点与失败恢复方式。

此仓库发布通用工作方法与代码；不包含原项目的科研数据、参考图片、AI 文件或 Blender 模型。它不是一键自动生成任意科研图的软件。

## 安装

下载本仓库 ZIP 并解压，将 `skills/blender-illustrator-figure-workflow` 整个文件夹复制到你的 Codex skills 目录：

- Windows：`%USERPROFILE%\.codex\skills\`
- macOS/Linux：`~/.codex/skills/`
- 如果配置了 `CODEX_HOME`，使用其下的 `skills/`。

重新开始会话后调用：

```text
使用 $blender-illustrator-figure-workflow，把验收通过的模型按原环境光渲染高清版本，更新当前打开的 Illustrator 总图和局部放大窗口，保留现有排版。
```

也可使用：

```text
使用 $blender-illustrator-figure-workflow，只裁掉当前总图底部纯背景空白，保留其他元素位置，保存后在软件中展示。
```

## 环境与验证边界

需要 Blender，以及可用的 Adobe Illustrator 和相应应用控制权限。Blender Python 用 Blender 自带解释器执行；JSX 用 Illustrator 执行。Windows 可使用 Illustrator COM，其他系统按可用的原生脚本入口运行。基础工作流来自 Blender 5.2 与 Illustrator 的实际编辑；其他版本应先在副本上检查 API 与色彩管理兼容性。

说明入口：[SKILL.md](skills/blender-illustrator-figure-workflow/SKILL.md)。脚本用法：[scripts.md](skills/blender-illustrator-figure-workflow/references/scripts.md)。脚本不替用户自动创建模型，也不自动修改或覆盖总图。

## 测试与许可证

运行 `python -m unittest discover -s tests -v` 检查渲染清单校验。当前 5 项测试覆盖路径解析、重复输出、禁止覆盖、无效分辨率和源文件/采样参数检查；不代表完整的 Blender/Illustrator 集成测试。

通用说明和代码采用 [MIT License](LICENSE)。Blender、Adobe Illustrator 等第三方软件遵循各自许可证，需自行安装。项目不隶属于 Nature 或任何期刊，也不代表期刊认证。
