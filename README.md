# 01_AI 视觉导演

当前技能：[`01_ai-visual-director`](skills/01_ai-visual-director/SKILL.md)，版本 **0.3.2**。

通过两轮索引确定场景与媒介表现，为 Midjourney 和 GPT Image 编写英文提示词。支持视觉探索、固定场景多机位、单条定稿、视频关键帧、选图细化和失败诊断。

## 独立技能安装

将本仓库的 `skills/01_ai-visual-director` 完整复制到 `~/.codex/skills/01_ai-visual-director`，保留其中的 `agents/`、`references/` 和 `scripts/` 等目录。

调用示例：

```text
使用 $01_ai-visual-director，从我的构想开始设计视觉方案并输出提示词。
```

## 仓库内容

- `skills/01_ai-visual-director/`：完整技能包，包含参考资料、校验脚本、测试和评估案例。
- `.codex-plugin/plugin.json`：保留插件安装兼容性，加载 `skills/` 下的技能。
- [更新记录](skills/01_ai-visual-director/CHANGELOG.md)。

新版技能替代原来的 `directing-midjourney-v8-2-visuals`，旧版本可在 Git 历史中查看。

## 验证

在仓库根目录运行：

```sh
python3 -B -m unittest discover -s skills/01_ai-visual-director/tests -v
```
