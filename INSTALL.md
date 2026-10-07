# 下载与使用 / Download and use

## Codex / ChatGPT Pets

1. 从 Releases 下载成品 ZIP 并解压，或下载独立 PNG。
2. 打开具备 Pets 工具的 Codex / ChatGPT 会话。
3. 附上完整 `spritesheet.png`，发送以下请求：

> 请使用 Pets 工具验证这张 v2 精灵图，将其创建为名为「银铃」的新宠物，并设为当前宠物。描述：银白长发、豆豆眼、棕色外套与紫色蝴蝶结的软萌伙伴。

4. 确认创建与启用结果。平台会为你的账户生成自己的宠物记录。

`pet.json` 是公开图集说明，方便开发者读取状态与方向。宿主导入时使用完整透明 PNG。

## 开发者集成

读取配置中的 `row`、`frames`、`durations_ms` 与 `directions_degrees`。单元位置为 `x = column × 192`、`y = row × 208`，尺寸为 192 × 208。

角度以屏幕坐标定义：0° 朝上，90° 朝右，180° 朝下，270° 朝左；中心位置使用待机状态。完整格式见 [ATLAS_FORMAT.md](docs/ATLAS_FORMAT.md)。

素材供个人非商业使用，条件见 [LICENSE-ASSETS.txt](LICENSE-ASSETS.txt)。

## English

Download the full PNG or extract it from the asset ZIP. Open a Codex / ChatGPT session with Pets tools enabled, attach the entire atlas and request:

> Validate this v2 sprite sheet with Pets tools, create a new pet named Yinling, and select it as my active pet. Description: A silver-haired companion with capsule eyes, a brown jacket and a purple ribbon.

Confirm creation and selection. The host creates a pet record for your account. The JSON manifest is developer documentation; the import artwork is the full transparent PNG.
