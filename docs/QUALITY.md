# 质量记录 / Quality record

记录版本：v1.0.0，2026-10-07。

## 已完成的检查

- Pets 工具预检接受最终透明图集，并已在制作账户中创建和启用。
- 图集尺寸、RGBA 通道、73 个有效帧和 15 个透明空格符合布局。
- 最终图集完成透明边缘去色处理，处理保留 alpha。
- 跳跃脚部轮廓从基线抬升 31 像素，落地回到相同基线。
- 十六方向身体中心相对待机最大偏移 5 像素，最大宽度比约 1.084。
- 三位独立 AI 审查者完成方向盲评，28 个水平与垂直判断一致通过。
- 最终动作、方向循环与待机—跳跃—待机过渡完成逐帧视觉检查。

公开指标摘要见 [quality-summary.json](quality-summary.json)。维护工具重新检查布局、透明单元格、边界、跳跃和素材哈希；方向含义与动作观感由视觉审查确认。

## 观感与后续改善

行走采用轻快弹跳节奏，部分迈步姿势重复。失落与检查动作主要通过眼睛和头部传达，小尺寸显示时更含蓄。跳跃采用五个关键姿势，呈现简洁的分段节奏。

方向连续性指标曾提示三处局部变化较大：157.5°→180°、270°→292.5°、337.5°→0°。逐帧视觉审查确认这些过渡连贯，记录保留在公开摘要中。

宿主应用的缩放、触发条件和播放时序会影响最终观感。

The final atlas passed the Pets preflight and was created and selected in the production account. Structural checks are reproducible locally; directional semantics and animation appearance were reviewed visually by AI reviewers. Movement has a springy cadence, failed/review expressions are subtle, and the five-pose jump is deliberately stepped. Host scaling and timing affect presentation.
