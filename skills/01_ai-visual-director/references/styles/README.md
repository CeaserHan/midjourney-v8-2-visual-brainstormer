# 风格卡

风格卡解决一个问题：选中的媒介和风格，**写进提示词后模型能不能画对**。media-modules 负责"有哪些选项"，风格卡负责"选中后怎么写才像"。

## 字段标记

风格卡的每条识别信号都带标记，决定它什么时候可以写入：

- `[M]`：媒介本身成立的最少识别信号。只要选了这个 M 就写，不受 V/Q/C 开放影响。
- `[K]` `[V]` `[H]` `[Q]` `[C]`：属于对应字段的示例。只有该字段已选或为 X、且所选内容与之相符时才写；字段为 0 时不写。

例：M 为版画、Q 选麻胶版、C0 时，写墨层与纸纹（[M]）和刻痕方向（[Q]），不写"黑色加朱红"（[C]）。Q0 时连刻痕也不写，因为那等于替用户选了凸版。

最少识别信号只能写这个媒介**所有子类共有**的特征。只属于某个版种、材料或工艺的特征，一律归入对应字段。

## 各媒介的最少识别信号

没有专门风格卡的媒介，至少写到这一层：

| M | 最少识别信号 |
|---|---|
| 写实摄影 | a real photograph，并写观察位置与距离 |
| 真人电影 | live-action film still，人物处在进行中的动作里 |
| 动画 | animation still；手绘、3D、定格等制作方式属于 Q，Q0 时不写 |
| 漫画 | comic panel，清楚的轮廓线；网点、排线、上色方式属于 V/Q，未选时不写 |
| 插画 | illustration，写线条或色块主导 |
| 油画 | oil painting, visible paint；画布、木板等支撑材料属于 Q，Q0 时不写 |
| 水彩／水粉 | transparent watercolor washes on paper / opaque gouache |
| 版画 | hand-pulled print on paper，可见墨层与纸纹；凸版、凹版、平版、孔版属于 Q，Q0 时不写版种，也不写刻痕、腐蚀线或网点 |
| CG | 3D render，写材质响应 |
| 平面设计 | graphic design，写版面结构（网格、留白、大形） |
| 实验艺术 | 写方法的可见证据（拼贴边缘、复印颗粒、像素错位） |

## 现有风格卡

- [printmaking.md](printmaking.md)：木刻／麻胶版画
- [comics.md](comics.md)：漫画（日漫、美漫、清线派、连环画）
- [fashion-editorial.md](fashion-editorial.md)：时尚杂志摄影
- [film-still.md](film-still.md)：电影静帧（同时服务 R4 关键帧）

## 加卡规则

按 [_template.md](_template.md) 写，每张 20–40 行。新卡必须在 `evals/cases.json` 里有对应用例，并有一次实际出图对照（有卡 vs 无卡）证明它改善了结果；连续两次对照没有差异的卡删除或重写。
