# 银铃 · Yinling Pet

[English](README.en.md) · [下载与安装](INSTALL.md) · [素材许可](LICENSE-ASSETS.txt)

银白长发、豆豆眼、棕色外套和紫色蝴蝶结的小伙伴。提供适配 Codex / ChatGPT Pets v2 格式的角色素材，包含 **9 组动作、16 个注视方向，共 73 帧**。

**工具代码 MIT 开源 · 角色素材个人非商业免费使用**

![银铃动作预览](docs/previews/all-states.gif)

## 下载

打开本仓库的 **Releases**，选择所需文件：

| 文件 | 用途 |
| --- | --- |
| `yinling-v1.0.0.zip` | 成品包：精灵图、配置、预览和许可 |
| `yinling-v1.0.0.png` | 完整透明精灵图，用于 Pets 工具导入 |
| `yinling-source-v1.0.0.zip` | 公开仓库源码与 73 个最终帧 |
| `SHA256SUMS.txt` | 下载文件的 SHA-256 校验值 |

也可以直接下载 [完整精灵图](assets/yinling/spritesheet.png)。导入步骤见 [INSTALL.md](INSTALL.md)。

## 动作与格式

待机眨眼、向右行走、向左行走、挥手、跳跃、失落、期待等待、专注思考、检查成果，以及顺时针排列的十六方向注视。

![注视方向](docs/previews/look-loop.gif)

透明 PNG 尺寸 **1536 × 2288**，8 列 × 11 行，每格 192 × 208。状态、时长和角度写在 [pet.json](assets/yinling/pet.json) 中。

## 仓库内容

```text
assets/yinling/       成品与公开配置
source/frames/       73 个最终透明帧
source/prompts/      制作提示词摘要
docs/previews/       GIF、MP4、动作与方向总览
scripts/             便携验证、组装、预览和打包工具
tests/               损坏图集、复现与发布包检查
.github/             自动检查、草稿 Release、协作模板
```

## 本地验证与打包

需要 Python 3.11+。

```sh
python -m pip install -r requirements.txt
python scripts/validate.py --verify-hash
python -m unittest discover -s tests -v
python scripts/build_release.py
```

发布文件生成在 `dist/`。复现图集及 GitHub 发布步骤见 [制作与发布指南](docs/DEVELOPMENT.md)。

## 来源与许可

图像通过 AI 图像生成制作，参考设计由发布者提供。来源记录见 [CREDITS.md](CREDITS.md)。提示词文件保存制作摘要，新的生成结果会随模型和参数变化。

工具代码、测试与文字文档采用 [MIT](LICENSE)；角色图像、源帧和视觉预览采用 [个人非商业素材许可](LICENSE-ASSETS.txt)。商业使用与修改版素材公开分发须另行取得书面许可。

欢迎通过 Issue 反馈，参与方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。
