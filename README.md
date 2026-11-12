# LOOP Video · 咨询师的 AI 获客短视频

> 作者：[易里 Yilee](https://github.com/yileeai) · AI 咨询师 · LOOP AI 获客

一套 Claude Code 技能，专门帮**咨询师、律师、财税顾问这类知识服务从业者**用 AI 做获客短视频。
不是通用的 AI 视频工具：每个模板都从真实的获客视频里拆出来，先讲清楚专业内容，再把人引到私信。

> 知识库部分（素材编译、客户诊断、咨询复盘、获客文案）在另一个仓库：[loop-skills](https://github.com/yileeai/loop-skills)。
> 两边配合用：`/content` 写好获客脚本，再交给这里的技能做成片。

## 视频形式

| 形式 | 技能 | 状态 |
|---|---|---|
| 出镜口播 + 代码动效 | `/speech-motion-edit` | ✅ 可用 |
| 不出镜（纯动效 / 图文成片） | — | 🚧 筹备中 |
| 数字人口播 | — | 🚧 筹备中 |

### `/speech-motion-edit` · 口播动效混剪

交给它一条对标短视频和你的口播原素材，它会：

1. **拆解对标**：画幅、分区、卡片、字幕、切换节奏、入场顺序。
2. **按逐字时间码做动效**：口播说到哪个词，画面就在哪一帧出现。信息卡逐层展开、连线生长、数字滚动、节点点亮、关键词高亮字幕。
3. **出片和验收**：先出静帧检查遮挡和溢出，再出全片，抽帧确认动效确实在动。也可以只对现成视频整片变速。

自带两个模板：

| 模板 | 样子 | 适合 |
|---|---|---|
| `render_split.py` 浅底分屏 | 上半屏米灰底图解，下半屏人像，字幕压在分界线 | 知识讲解、热点解读、政策拆解 |
| `render_motion.py` 黑金信息卡 | 整屏底片 + 近黑信息卡 + 渐隐网格 | 案例拆解、数据对比、架构说明 |

## 安装

需要：[Claude Code](https://claude.com/claude-code)、Python 3、[Pillow](https://pypi.org/project/pillow/) ≥ 10、[FFmpeg](https://ffmpeg.org)。
没有文字稿时还要装 faster-whisper 做转录，说明见 `skills/speech-motion-edit/references/production.md`。

```bash
git clone https://github.com/yileeai/loop-video.git
```

Windows：

```bat
loop-video\install.bat
```

macOS / Linux：

```bash
bash loop-video/install.sh
```

默认装到你的个人技能目录（`~/.claude/skills/`），在任何文件夹打开 Claude Code 都能用。
想只装进某个库或项目，就在后面加上路径，例如 `install.bat "D:\Obsidian\根据地"`。

装好后，在 Claude Code 里说「用这两条视频做一条同款」，或者输入 `/speech-motion-edit`。

> **视频成品不要放进知识库**：原素材和成片放本地素材盘或网盘，库里只记路径。

## 目录

```
loop-video/
└── skills/
    └── speech-motion-edit/
        ├── SKILL.md            技能说明（Claude 读）
        ├── references/         制作流程、参数、示例时间线
        └── scripts/            render_split.py · render_motion.py · asr.py
```

## 许可

本仓库采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)，全文见 [LICENSE](LICENSE)：

- ✅ 可以免费学习、使用，按自己的行业随意修改；
- ✅ 用它给**自己的生意**做获客视频完全可以，视频归你，发布时不需要署名；
- ✅ 转载或分享改编版技能时，注明出处「易里 Yilee · LOOP」并附本仓库链接；
- ❌ 不得商用：不能打包售卖，也不能放进付费课程、付费社群或付费代做服务；
- 🔁 改编后公开的版本，也必须用同样的协议。

**商业合作或授权**：欢迎联系 [易里 Yilee](https://github.com/yileeai)。
