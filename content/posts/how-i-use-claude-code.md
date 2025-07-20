---
title: "使用 Claude Code 体验提升的小技巧"
date: "2025-07-20"
tags: ["knownenoughtobedangerous"]
description: "从工作流程到实战技巧，分享我使用 Claude Code 进行开发的心得体会"
---

自从开通了 Claude Code Max 5x 计划以来，开发方式已经发生了极大变化。在这里简单整理了一下自己的使用流程，其中的技巧也适用于 Gemini CLI 和 Open Code。

### CLAUDE.md

如果有什么东西需要 Claude Code 在每轮对话中记住的话，就可以把它放进 `CLAUDE.md` 文件中。例如我有个项目用到了 `SwiftData`，在项目根目录下的 `CLAUDE.md` 中我就留下了这样的描述，提醒 Claude Code 在功能实现过程中不要把数据结构搞坏了，如果出现了它认为必要的改动，也应该设计好数据迁移的计划：

> When modifying any file containing `import SwiftData`, caution should be exercised. If it's a "must-have" operation, think hard about how to migrate the data.

如果是各项目通用的注意事项，则可以在 `~/.claude/CLAUDE.md` 中提及。比如我会让 Claude Code 不要生成 300 行以上的文件：

> Make sure the code related file you created or modified are no longer than 300 lines of code.

### `/clear`

准确的上下文对 Claude Code 输出质量影响非常显著，无论是对话需要 `/compact`，还是大任务的修修补补，都应该多用 `/clear` 来为 Claude Code 提供一个完整可用的上下文。这种操作习惯了以后，也会在派活儿给 Claude Code 时有个拆解任务的前置动作，否则很可能一个大而模糊的任务丢给 Claude Code，导致上下文被无关内容占用。

### `GitHub CLI`

Claude Code 非常善于使用 Github CLI，这一点在他们的官方教程中也有提及。网上有很多人会推荐让 Claude Code 在本地把任务拆解了放在一个 markdown 文件中， 倒也是没什么问题。但这种事情我更习惯让 `Claude Code` 用 `gh` 命令来创建一个 issue doc。这样我还能让其他的 agent 很方便地去 review 这份计划，并且同样通过 `gh` 来添加评价乃至修订。不过老实说随着我习惯性给 Claude Code 的指令越来越小且具体，已经很少这么做了。

### 任务分解

如果自己也不太清楚任务如何分解，可以通过 "如果我想实现 X，那么我应该先解决哪些问题？" 这样的 decomposition prompt 技巧来让 Claude Code 帮助分解任务。使用这个 prompt 的时候可以用 `shift + tab` 来切换到 plan mode，这样 Claude Code 不会修改任何文件。体感上 plan mode 配合前面提到的 “我想实现 X，实现之前我应该先解决哪些问题？” 的 prompt，然后再让 Claude Code 去实现代码效果特别好。

### 自定义 command

可以在 `~/.claude/commands/` 目录下放置自己工作流中常用的 prompt，除了[官方实例](https://www.anthropic.com/engineering/claude-code-best-practices)中提到的 Fix the GitHub issue 之外，自己很常用的就是：

> commit in logical chunks and push

用了之后就很久没有自己提交代码了。

以上都是一些小技巧但确实在工作流程中产生了体感上的差异，后续会持续更新在这里。但感觉随着 AI 的演化，可能很快各种技巧就没用了吧...
