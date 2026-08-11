# Midjourney V8.2 兼容规则

核验基准：2026-08-10。功能、界面或费用可能更新；用户要求精确的当前参数事实时核对官方文档，不凭记忆猜测。

## 1. 结构化提示词

- 工作流面向 Midjourney V8.2。
- 把结构落实为信息顺序，最终只输出一段无字段标题的英文视觉描述。
- 按任务需要依次写入非空部分：媒介与 K → 主体、场景和事件 → 多人物可见分离 → 观察与构图 → 年代和地点证据 → 已选 V/H/A/Q/C 的可见结果。
- 让每条提示词完整独立；不得依赖同组标题、上一条提示词或代码块外说明才能成立。
- 开放字段直接省略，不写占位词，不为补齐顺序增加内容。

内部可用以下骨架检查，但不得把方括号或字段名交付给用户：

```text
[medium and selected K] [subject, scene, event] [subject separation] [observation and composition] [visible era/place evidence] [selected visual treatment]
```

## 2. 语言规则

- 使用清晰、具体、相对精简的英文可见描述。
- 优先写名词、动作、位置、空间关系、边缘、纹理和光色结果。
- 作者或流派不能替代主体、场景和构图；保留用户选中的姓名，同时补充相关可见特征。
- 不写 `please create`、`make it look like` 等发布命令。
- 不写 `Goal:`、`Scene:`、`Must preserve:`、`Constraints:`、`Change only:` 或 `Keep unchanged:`。
- 不堆叠 `photorealistic`、`hyperrealistic`、`ultra realistic` 或空泛质量口号。
- 不使用 V8 不支持的文本 Multi-Prompt `::`。
- 不把其他版本专属功能当作 V8.2 的确定能力。
- 不虚构 Image URL、Style Reference 代码、Profile ID 或引用权重。

细化或变体仍输出完整提示词，正向重述修改后的最终画面。代码块外可以说明唯一变化，但代码块内不得使用 GPT Image 2 编辑协议，也不得依赖 `same`、`original`、`source image`、`preserve`、`unchanged` 或 `identical` 说明未变化内容。

## 3. 参数分离

英文提示词不得包含任何以连续双短横线开头的 Midjourney 参数，包括但不限于 `--ar`、`--v`、`--raw`、`--s`、`--no`。

默认不显示官网设置。只有用户主动询问时，才在提示词代码块之外提供 Version、Aspect Ratio、Standard/HD、Raw、Stylization、Weirdness、Variety、Personalization 和 References 建议。

多方案比较使用同一组官网设置，避免设置变化掩盖内容或构图差异。所有数值都标为实验起点，不声称唯一最佳值。

## 4. 参考图策略

- **分析用途**：用户上传图片时默认先分析内容、构图、光色或风格，不自动把它当作生成引用。
- **Image Prompt**：影响内容、构图和颜色。适合保持场景身份，但可能把新结果拉回原图观察位置。
- **Style Reference**：影响风格、材质、色彩和光线，不用于复制具体人物或物件。
- **内容一致性**：没有适用于 V8.2 且经过核验的能力时，不承诺精确人物、服装、物体或建筑复现。
- **多构图探索**：引用图强烈控制构图时，先提示它可能抵抗新视角。

只有用户提供真实图片、URL、代码或 ID 时才写入引用流程。

## 5. 官网设置实验起点

只在用户主动询问时使用：

| 媒介 | 常见画幅起点 | Raw | Stylization | 模式 |
|---|---|---|---:|---|
| 克制纪实摄影 | 3:2 | 开 | 25–60 | Standard 探索，HD 定稿 |
| 作者型/时尚摄影 | 3:2 或 2:3 | 开 | 60–150 | Standard 探索，HD 定稿 |
| 建筑与室内摄影 | 3:2 | 开 | 25–75 | Standard 探索，HD 定稿 |
| 真人电影 | 16:9 或用户画幅 | 开 | 50–75 | Standard |
| 电影/游戏气氛图 | 16:9 | 按需 | 125–175 | Standard |
| 角色概念 | 2:3 | 按需 | 100–150 | Standard |
| CG/插画 | 4:5 | 关 | 175–250 | Standard |
| 油画/水彩 | 4:5 | 关 | 125–200 | Standard |

Weirdness 默认从 0 开始，只有用户明确追求异常视觉时再做低幅度对照。Personalization 默认关闭；用户主动要求并已有合适配置时再开启。

## 6. 官方来源

- V8.2 发布：https://updates.midjourney.com/version-8-2/
- Prompt Basics：https://docs.midjourney.com/docs/prompts
- Creating on Web：https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web
- 参数总表：https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List
- Image Prompts：https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts
- Style Reference：https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference
- Personalization：https://docs.midjourney.com/hc/en-us/articles/32433330574221-Personalization
