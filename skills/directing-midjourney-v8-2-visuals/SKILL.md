---
name: directing-midjourney-v8-2-visuals
description: Directs two-round, indexed visual prompting for Midjourney V8.2 and GPT Image 2, from an era-and-place idea through scene choices, medium-specific art direction, prompt generation, fixed-scene camera execution, selected-image refinement, and failure diagnosis. Use for photography, live-action cinema, game or film concept art, illustration, oil painting, watercolor/gouache, and CG; also use for dynamic style/movement/artist/equipment recommendations, historical reconstruction, multi-character separation, or cross-model prompt adaptation.
---

# AI 视觉导演

## 目标

把年代、地点、自然语言构想、已有提示词或参考图片发展成可选择、可执行、可继续细化的视觉方案。第一次生成采用两轮选择：先确定场景与任务，再根据媒介确定作品类型和美术表现。完成第二轮后直接交付，不发送第三张确认卡。

只把用户明确选择、连续性必需事实或用户明确交给 AI 视觉导演设计的字段写入约束。未选择和 `0` 字段保持开放，并在最终英文提示词中完全省略，让目标出图模型在生成时自然落实；不得写成 `style left open`、`unspecified artist` 或 `unconstrained equipment`。只有用户主动选择 `X` 或明确授权 AI 设计相关字段时，AI 视觉导演才选择具体答案、公开并锁定；不得为了完整、推荐或视觉协调把开放字段自动转成 `X`。

## 必读与按需读取

每次任务先完整读取：

- [intake-and-routing.md](references/intake-and-routing.md)：两轮索引、状态语义和跳过规则。
- [output-contract.md](references/output-contract.md)：选择卡与各阶段交付格式。
- [model-adapters.md](references/model-adapters.md)：目标模型分流和输出边界。

再按任务读取：

- 第二轮选择：读取 [media-modules.md](references/media-modules.md) 的当前媒介章节。
- Midjourney V8.2：读取 [midjourney-v8-2.md](references/midjourney-v8-2.md)。
- GPT Image 2：读取 [gpt-image-2.md](references/gpt-image-2.md)。
- 摄影或真人电影执行：读取 [photography-domains.md](references/photography-domains.md)。
- 概念美术、插画、油画、水彩或 CG 执行：读取 [visual-domains.md](references/visual-domains.md) 的当前媒介章节。
- `R1 视觉探索`：读取 [visual-direction-design.md](references/visual-direction-design.md) 与 [camera-and-composition.md](references/camera-and-composition.md)。
- `R2 固定场景执行`：读取 [camera-and-composition.md](references/camera-and-composition.md)。
- 作者、摄影师、导演、杂志、机构或工作室推荐：读取 [reference-translation.md](references/reference-translation.md)。
- 两个或更多主要人物、群众或复制问题：读取 [multi-subject-identity.md](references/multi-subject-identity.md)。
- 第二轮完成或发现不兼容选择：读取 [conflict-checking.md](references/conflict-checking.md)。

## 判断任务阶段

- **第一轮选择**：用户提出年代、地区或初步构想，但场景与任务仍有高影响缺口。
- **第二轮选择**：媒介已经确定，需要列出该媒介的作品类型、画风、流派、作者、过程与光色。
- **R1 视觉探索**：默认十二个内容与视觉发现不同的方向；1–6 可控，7–12 大胆。
- **R2 固定场景执行**：默认六个内容完全相同、观察与构图真正不同的版本。
- **单条定稿**：信息已经收敛，只需要一条提示词。
- **细化**：用户提供生成图或已选方案并说明保留与改变。
- **诊断**：用户报告双胞胎、复制、雷同、漂移、风格错误或提示词失效。

细化、诊断和已有提示词改写不得重新启动两轮选择。用户已经回答的字段不得重复询问。

## 核心工作流

### 1. 接受并预填自然语言

接受一句话、索引串、已有提示词、作品名称或图片。提取目标模型、工作模式、真实性、年代、地区、时间、具体地点、人物、事件、天气、媒介、用途及已有第二轮选择。把明确内容列为“当前锁定”，不要求用户重写成表格。

### 2. 第一轮：场景与任务

用户从年代和地区开始时，一次列出仍未确定的：`Z R U T L P E W M O`。每个适用字段提供约 8–12 个动态选项、`0 开放`、适用时的 `X 由AI设计` 和一个 `⭐` 推荐。选择卡说明：`0` 把该字段留给目标出图模型，`X` 把该字段交给 AI 视觉导演先行设计。M 只列广义媒介；街头纪实、编辑摄影、可玩空间、历史画等专业类型必须留到第二轮 K。

第一轮不询问横竖画幅、留白或版面方向。普通街头纪实仍显示 E，但推荐 `E0 自然发生／不限定行为`；不影响室内的天气仍显示 W，但推荐 W0。

### 3. 第二轮：媒介专属表现

媒介确定后，一次列出当前媒介适用的 `K V H A Q C`：

- K：作品类型／交付形态；
- V：最终可见的美术表现画风；
- H：历史传统／流派；
- A：作者参考；
- Q：器材、材料或制作过程；
- C：光线与色彩。

从 [media-modules.md](references/media-modules.md) 动态生成选项，不使用固定名单。各字段职责不得混合。第二轮回复后没有真实冲突就直接生成。

### 4. 维护约束账本

内部记录：

```text
字段 | 用户选择 | 来源 | 锁定/开放 | 是否写入提示词
```

`0`、未选择或留空表示开放：AI 视觉导演不得静默具体化，最终英文提示词完全省略该字段，由目标出图模型在生成时自然落实。`X` 只在用户主动选择或明确授权时生效；AI 视觉导演必须选择具体答案并在交付前公开，随后才可写入提示词。Z 是输出协议，不提供 X；Z0 只允许继续视觉方案，交付最终英文提示词前只补问目标模型。

### 5. 检查冲突

第二轮后检查年代、地点、媒介、作品类型、作者、过程、光色、人物和目标模型。轻微措辞问题内部修正；会改变用户意图时只询问冲突字段，不重发选择卡。

### 6. 设计内容与构图

R1 先设计十二个内容方向，再为每个方向选择最能证明其发现的观察方式；不得把换焦段或换形容词当作新方向。R2 固定人物、地点、时间、天气和事件，任意两版的构图签名至少三个维度不同。

非摄影媒介把镜头语言转译为画面尺度、观察高度、空间方向、透视、重叠平面、负空间、边缘和材质语言。

### 7. 分离多人身份

两个或更多主要人物时建立人物账本。每人至少在位置、形体、服装剪影、动作和方向中的三项不同。群众保持较小、较远或部分遮挡，不升级为第二组主角。

### 8. 转译作者参考

保留用户选中的作者姓名，同时补充与当前场景相关的可见特征。不得只写 `in the style of [name]`；也不得因为选择作者而自动锁定未选择的流派、制作过程或光色。

### 9. 适配目标模型

先完成同一份内容与视觉约束，再应用 [model-adapters.md](references/model-adapters.md)。只改变表达结构，不重新设计内容：

- Midjourney V8.2：按媒介、场景、人物、构图、时代证据和已选美术表现组织信息，输出一段无字段标题、无制作命令、无参数的连贯英文视觉描述。
- GPT Image 2：简单任务使用清楚的自然段；复杂场景、精确布局、多人物、多图输入或编辑任务使用必要的制作标签。编辑任务明确 `Change only` 与 `Keep unchanged`。

适配阶段不得新增内容或审美约束。平台设置只在用户主动询问时另行提供。

### 10. 细化与诊断

细化时建立“保留／加强／改变／删除／允许试验”卡，默认输出四个单变量版本。诊断时指出具体触发短语、结构根因和最小修复；只在用户要求时重写整组。

## 交付前自检

- 是否处于正确阶段，且没有重复询问已知字段？
- 第一轮和第二轮是否各自一次展示全部适用字段？
- K、V、H、A、Q、C 是否职责清楚且没有同项跨栏？
- `0` 和未选字段是否没有进入提示词？
- 未选用途是否没有被改写成个人创作、商业广告、编辑刊物或其他交付目的？
- `X` 是否公开了 AI 的具体决定？
- 第二轮后是否直接交付，没有第三张确认卡？
- R1 是否恰好十二条且内容差异成立？
- R2 是否保持内容固定且构图签名真正不同？
- 多人物是否具有独立身份、动作和尺度层级？
- 作者姓名是否保留并完成可见特征转译？
- 目标模型语法是否正确，且没有跨模型污染？
- 是否只在用户主动询问时提供平台设置？

不通过时在交付前改写。
