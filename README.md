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

一个技能就是一个文件夹，核心是里面的 `SKILL.md`。装技能 = 把 `skills/speech-motion-edit` 这个文件夹放进你的 AI 软件认的技能目录。下面三种装法任选一种。

### 方式一：让 AI 自己装（推荐，Claude Code）

把下面这段话原样发给你的 AI：

> 请帮我安装这个技能：https://github.com/yileeai/loop-video 。把仓库里的 `skills/speech-motion-edit` 整个文件夹复制到我的个人技能目录（Claude Code 是 `~/.claude/skills/`）。然后检查我电脑上有没有 Python 3、Pillow 10 以上版本和 FFmpeg，缺什么就帮我装好。装完运行 `python -c "import PIL; print(PIL.__version__)"` 和 `ffmpeg -version` 确认。

### 方式二：下载压缩包，双击安装（不用会 git）

1. 在本页点绿色的 **Code** 按钮 → **Download ZIP**，解压。
2. Windows 双击 `install.bat`；macOS / Linux 在终端运行 `bash install.sh`。

会用 git 的话，也可以：

```bash
git clone https://github.com/yileeai/loop-video.git
```

脚本默认装到个人技能目录（`~/.claude/skills/`），在任何文件夹打开 Claude Code 都能用。
想只装进某个库或项目，就在后面加上路径，例如 `install.bat "D:\Obsidian\根据地"`。

### 方式三：WorkBuddy 等其他 AI 软件

在软件的技能管理里新建或上传技能，把 `skills/speech-motion-edit` 整个文件夹传上去；也可以直接对它说「帮我从这个链接安装技能」。
各软件菜单不同，以软件自己的说明为准。**出片需要在你电脑上运行 Python 和 FFmpeg**，软件不能执行本地命令的话，请改用 Claude Code 出片。

### 装完先确认环境

视频技能比普通技能多一道门槛：要在你自己的电脑上跑程序出片。需要三样东西：

| 需要 | 做什么 | 检查命令 |
|---|---|---|
| Python 3 | 运行出片脚本 | `python --version` |
| [Pillow](https://pypi.org/project/pillow/) ≥ 10 | 逐帧画图 | `python -c "import PIL; print(PIL.__version__)"` |
| [FFmpeg](https://ffmpeg.org) | 合成视频和声音 | `ffmpeg -version` |

没有文字稿时，还要装 faster-whisper 做转录（第一次运行会下载约 500MB 模型），说明见 `skills/speech-motion-edit/references/production.md`。
不会装没关系，把上表发给你的 AI，让它帮你装。

### 第一次用

1. **重启 AI 软件**，让它读到新技能。
2. 把对标视频和你的口播原素材交给它，说「用这两条视频做一条同款」，或输入 `/speech-motion-edit`。
3. **先让它出一张静帧**，能出来说明环境没问题，再出全片。
4. Windows 用黑金模板时，提醒 AI 加上 `--font C:/Windows/Fonts/msyhbd.ttc`，否则中文显示不出来（浅底分屏模板会自动找微软雅黑）。

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
