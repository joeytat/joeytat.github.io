+++
title = "参加 Apple 开发者线上活动是什么样的体验？"
date = "2022-03-28T00:00:35"
author = "Joeytat"
tags = ["SwiftUI"]
description = "记录一下收获到的与 SwiftUI 相关的资料，与一条来自苹果工程师的学习路线。"
+++

从朋友圈看到思琦发了一个《使用 SwiftUI 打造卓越体验》的 Apple 开发者线上活动的报名链接，刚好最近参与的项目也在大规模使用 SwiftUI 就报名了，即使时间很不凑巧是工作日（另一报名要求是必须要有中国区的开发者账号）。

活动分两天第一天主要是一些 SwiftUI 的介绍，SwiftUI 对数据的处理和布局的一些要点。第二天是社区开发者交流。

技术细节后面可以分好几篇博客来描述，但总的来说技术相关的收获其实和自己去看 WWDC 差不多。并且由于长期以 2x 速度观看这类视频，刚开始还出现了一些不适应。但想着这是来自苹果的开发者的分享，还是管住了想拿起手机的手，毕竟机会难得。

事实证明确实认真观看还是有收获，主要是以下几点：

- 知道了一些 SwiftUI 相关的 Xcode 快捷操作，比如 Preview 和代码其实是可以相互影响的。Library 中可以搜索 `ViewModifier` 等等。
- 来自苹果的工程师对 SwiftUI 这样响应式 UI 编写方式的数据流思考的建议。
- 一些编写 SwiftUI 代码时能够让渲染引擎更高效的建议。

除了上面开发者分享的内容之外，最重要的是可以提出一些自己在使用 SwiftUI 时遇到的问题，感觉只要描述得够清楚并且和本次活动主题相关，那么都能够得到苹果开发者的解答，虽然受形式或时间限制，答案并不一定完整，但当一个 SwiftUI 的疑问是由苹果的工程师解答时，即使只是关键字的指引也能起到画龙点睛的作用（比如 `StateObject` 与 `ObservedObject` 的差异）。

第二天更多的是听社区开发者的一些交流，收获到了不少之前并不知道的资料。一并列在下方。

ps：感觉参加这次活动对自己来说还有一个副作用就是，由于资料的推荐者有足够的可信度，并且提供了一个可靠的学习路线，所以会用格外的认真来对待它们。

Swift UI 的入门指引
- [WWDC - Introduction to SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10119/)
- [WWDC - SwiftUI Essentials](https://developer.apple.com/videos/play/wwdc2019/216/)
- [十个很有代表性的 Playground](https://developer.apple.com/tutorials/sample-apps)
- [交互式的 SwiftUI 入门教程](https://developer.apple.com/tutorials/swiftui)
- [使用 SwiftUI 构建完整 App 的交互式教程](https://developer.apple.com/tutorials/app-dev-training)

SwiftUI 数据处理要素
- [WWDC - Data Essentials in SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10040/)
- [WWDC - Demystify SwiftUI](https://developer.apple.com/videos/play/wwdc2021/10022)
- [状态与数据流](https://developer.apple.com/documentation/SwiftUI/State-and-Data-Flow)
- [如何管理 App 中的模型数据](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [如何管理 UI 状态](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)

SwiftUI 布局和渲染
- [WWDC - What's new in SwiftUI](https://developer.apple.com/videos/play/wwdc2021/10018/)
- [WWDC - Stacks, Grids, and Outlines in SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10031/)
- [WWDC - Add rich graphics to your SwiftUI app](https://developer.apple.com/videos/play/wwdc2021/10021/)
- [WWDC - Building Custom Views with SwiftUI](https://developer.apple.com/videos/play/wwdc2019/237/)
- [布局容器](https://developer.apple.com/documentation/swiftui/layout-containers)
- [集合布局容器](https://developer.apple.com/documentation/swiftui/collection-containers)
- [图像与绘制](https://developer.apple.com/documentation/swiftui/drawing-and-graphics)

用 SwiftUI 打造 watchOS app
- [WWDC - SwiftUI on watchOS](https://developer.apple.com/videos/play/wwdc2019/219/)
- [WWDC - Build complications in SwiftUI](https://developer.apple.com/videos/play/wwdc2020/10048/)
- [打造 watchOS App](https://developer.apple.com/documentation/example-articles/building_a_watchos_app)
- [如何利用 SwiftUI 以及手表特定功能打造复杂 app 的代码示例](https://developer.apple.com/documentation/watchosapps/developing_a_user_interface_with_swiftui)

社区开发者提及
- [文档生成工具 - DocC](https://developer.apple.com/documentation/docc#Overview)
- [WWDC Digital Lounges 中的开发者问答整理](https://swiftui-lab.com/random-lessons/)
- [SwiftUI Companion - 交互式 SwiftUI API 文档工具](https://swiftui-lab.com/companion/)
