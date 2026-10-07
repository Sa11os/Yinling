# 制作、验证与发布

## 本地维护

需要 Python 3.11+ 与 Pillow。推荐创建独立环境：

```sh
python -m venv .venv
```

激活环境后：

```sh
python -m pip install -r requirements.txt
python scripts/validate.py --verify-hash
python -m unittest discover -s tests -v
python scripts/build_release.py
```

工具从自己的文件位置定位仓库，支持带空格的目录路径。产物写入已忽略的 `dist/`。

## 从最终帧复现

```sh
python scripts/assemble.py --output dist/rebuilt-spritesheet.png
python scripts/validate.py --atlas dist/rebuilt-spritesheet.png
python scripts/render_previews.py --output dist/previews
```

组装工具按 `assets/yinling/pet.json` 读取 73 个最终帧，将完整 RGBA 单元格粘贴至同样的坐标。测试比较重建图集与成品的全部像素。PNG 编码字节可能随 Pillow 版本变化，官方成品的 SHA-256 记录于配置。

`source/prompts/` 保存制作摘要与方向规则，适合理解角色制作。重新生成图像时需提供有权使用的参考，结果会随模型与参数变化。最终帧用于复现已发布成品。

如维护新的素材版本，请同步最终帧、图集哈希、版本、日期、预览、质量记录与 CHANGELOG，并重新运行检查。

## 发布包

`build_release.py` 输出：

- `yinling-v1.0.0.zip`：精灵图、公开配置、安装说明、预览、署名及许可。
- `yinling-source-v1.0.0.zip`：完整公开文件树、源帧、文档、测试和工具。
- `yinling-v1.0.0.png`：原始成品图集。
- `yinling-v1.0.0.manifest.json`：公开配置。
- `SHA256SUMS.txt`：上述文件的校验值。

工具使用明确的公开文件列表，并扫描文本中的账户文件标识、个人机器绝对路径和凭据特征。生成阶段的素材、账户上传记录和本地依赖保存在已忽略的私有工作目录。ZIP 文件顺序、时间与权限固定；同一环境连续打包的结果一致。

## 上传 GitHub

1. 补齐 [CREDITS.md](../CREDITS.md) 中参考图的原作者、来源与授权记录。
2. 在 GitHub 创建仓库，名称建议 `yinling-pet`。
3. 将源码 ZIP 解压后的全部文件上传到仓库，包括隐藏的 `.github/`、`.gitignore` 和 `.gitattributes`。
4. 或在本地添加这些公开文件并提交，连接自己创建的 GitHub 仓库后推送 `main`。
5. 首次公开版本使用标签 `v1.0.0`。命令行推送示例：

```sh
git tag v1.0.0
git push origin v1.0.0
```

推送标签后，GitHub Actions 执行验证、测试与打包，并生成附带下载文件的 **Release 草稿**。检查标题、说明、许可和附件后发布。若通过网页上传源码，可在 Releases 创建草稿并手动添加 `dist/` 中的五个文件。

常规检查使用 Windows 与 Linux。自动发布在 Linux 执行，采用仓库自带的 `GITHUB_TOKEN`，所需权限为写入仓库内容。

工作流依据 [GitHub 官方 Release 文档](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)、[checkout](https://github.com/actions/checkout) 与 [setup-python](https://github.com/actions/setup-python) 编写。推送到 GitHub 后可在 Actions 查看运行结果。

## English

Install the pinned requirement, validate the atlas, run unittest discovery and build the release. Assembly from final frames reproduces the image pixels. Fresh AI generation can vary.

Before publication, complete reference credits and authorization records. Upload the full source tree to a new repository, or commit and push it with Git. Pushing the matching version tag runs validation and creates a draft GitHub Release with download attachments. Review that draft before publishing. Repository CI covers Windows and Linux; release packaging runs on Linux.
