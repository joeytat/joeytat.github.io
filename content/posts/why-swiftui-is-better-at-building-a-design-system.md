---
title: "构建易维护的 Design System: 为什么 SwiftUI 会是更好的选择"
date: "2023-06-02"
tags: ["Swift", "SwiftUI"]
description: "通过 SwiftUI 构建 Design System 有哪些优势"
---

`SwiftUI` 自 iOS 13 发布以来，虽然已经面向公众近 4 年，但由于在实现复杂布局时的性能不佳，以及因其内置组件的底层实现变更（iOS 16 上 `List` 的底层实现从 `UITableView` 改成了 `UICollectionView` ），导致开发者们原本良好运行代码随系统升级被破坏了。iOS 14 之前 SwiftUI 的开发者体验也让人一言难尽。尽管有很多的槽点，但我们还是能发现社区整体上还是比较接纳 SwiftUI。所以如果你对 SwiftUI 还有所犹豫，不清楚为何要使用它，这篇文章或许能够带来一些新的想法。

本篇文章主要是想要通过 Design System 为切入点，同大家讨论相比起 UIKit，为什么更推荐使用 SwiftUI 来实现大多数业务场景下的 UI 组件。

首先简单概括一下 Design System 是什么，Design System 是一个包含了设计原则、组件库和代码资源等系统化的指导，旨在促进团队间的协作和提高项目的一致性。它可以帮助团队更快速、高效地构建应用程序，同时确保应用程序的外观和交互保持一致。

接下来就进入正题，从以下几点来探讨一下通过 SwiftUI 构建 Design System 有哪些优势。

- 声明式语法会更具有可读性和易于实现
- 内建的一致性和统一性表达
- 单向数据流带来的可预测性
- 与 Design System 有更相似的哲学思想

## 声明式语法会更具有可读性和易于实现

首先从实现和维护成本上来说，SwiftUI 与 Apple 现有的 UIKit 和 AppKit 不同，SwiftUI 采用了声明式语法构建 UI。由于声明式语法更关注于描述 UI 的最终效果，而不是具体实现方式。这使得通过声明式语法编写的 UI 组件更具可读性，有助于团队更好地协作实现 Design System。

```swift
// SwiftUI
VStack(spacing: 20) {
    Text("Hello")
        .font(.largeTitle)
    Text("World")
        .font(.largeTitle)
}
.foregroundColor(.blue)

// UIKit
let stackView = UIStackView()
stackView.axis = .vertical
stackView.spacing = 20

let helloLabel = UILabel()
helloLabel.text = "Hello"
helloLabel.font = UIFont.systemFont(ofSize: 34)
stackView.addArrangedSubview(helloLabel)

let worldLabel = UILabel()
worldLabel.text = "World"
worldLabel.font = UIFont.systemFont(ofSize: 34)
stackView.addArrangedSubview(worldLabel)

stackView.backgroundColor = .blue
```

除了代码数量上的差距，我们还可以在 SwiftUI 示例中通过代码结构就直观地感受到 UI 组件是如何被排列的。

## 内建的一致性和统一性表达

在 SwiftUI 中，我们可以通过 `View Modifier` 来实现对 UI 组件的统一性表达。

```swift
// SwiftUI
Button("Primary") {
    // action
}
.buttonStyle(PrimaryButtonStyle())

Button("Secondary") {
    // action
}
.buttonStyle(SecondaryButtonStyle()) // 当 Primary， 或 Secondary style 发生变化时，所有使用了这两个 style 的按钮都会被自动更新

// UIKit
let primaryButton = UIButton()
primaryButton.setTitle("Primary"， for: .normal)
primaryButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
primaryButton.backgroundColor = UIColor.blue
primaryButton.layer.cornerRadius = 5

let secondaryButton = UIButton()
secondaryButton.setTitle("Secondary"， for: .normal)
secondaryButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
secondaryButton.backgroundColor = UIColor.gray
secondaryButton.layer.cornerRadius = 5
```

通过代码我们可以看到 SwiftUI 预定义的设计规范，使开发者更易于表达和保证 Design System 的统一性。

虽然开发者也可以对 UIKit 的 UI 组件进行封装，实现类似 SwiftUI View Modifier 的效果。但是 SwiftUI 的 View Modifier 是内在耦合的，会天然具有更好的一致性。而对 UIKit 进行二次封装，仍需依赖于开发者自觉遵循设计规范，难免会产生疏忽的情况，影响最终 UI 的一致性。

## 单向数据流带来的可预测性

SwiftUI 所编写的 UI 组件更具有可预测性。体现在其遵循单向数据流原则，这样可以减少因为状态管理复杂性导致的 UI 错误。同时 UI 组件的样式是通过高阶函数或组合来创建的，而不是通过副作用或隐式规则创建，这使得开发者更容易识别组件会具备哪些样式及其来源。

相比之下 UIKit 作为命令式 UI 框架，其 UI 渲染过程则相对复杂和难以预测。

- 状态变化会导致难以跟踪的副作用，这使 UI 更易出错且难以调试。
- 样式规则由开发者自行定义并应用，存在较大随意性，阅读和理解起来也更加困难。
- 样式的来源和应用不像 SwiftUI 那样清晰，需要开发者自行理清各个样式规则之间的关系，以确保 UI 的正确性。

## 更相似的哲学思想

SwiftUI 中组合和函数式的思想与 Design System 中原子组件和组合的原则相吻合。

- 两者都倾向于构建出小的、自洽的单位，然后通过组合来创建更为复杂的结构，SwiftUI 中的视图和 Modifier 就是这种单位和组合的体现。
- 组件和函数都是可以是通用的或定制的，同时可以将其重复使用或组合。在 SwiftUI 中，我们可以构建出通用的 Modifier 和视图，也可以为某一具体视图定制特有的 Modifier。
- 当改变基础单位(如字号，间距等基础单位)会以可控方式影响所有组合。如果我们改变一个 Modifier 的行为或属性，所有应用该 Modifier 的视图将会相应改变。这使得在设计系统中调整细节时，更易预测和控制其影响范围。

而相比之下，UIKit 作为命令式框架，其 UI 构建方式则相对零散和随意:

- 构建 UI 时，开发者自行决定组装哪些控件和设置何种属性，难以遵循统一的组合规则。
- 没有类似 Modifier 的机制，每个视图的样式都需要单独设置，无法在多处重复使用。这使得调整样式时，需要逐个修改每个视图，难以高效地应用设计变化。
- 属性的变化并不一定会影响所有相关视图，需要开发者自己再逐个对应用的视图做出修改。这加大了设计系统维护的难度。

## 最后

还需要说明的是，本文只是想探讨在实现移动平台的 Design System 时相比起 UIKit，SwiftUI 所具有的一定优势。

在某些复杂的场景下，UIKit 这样命令式的 UI 框架的灵活性和性能可能会更强。所以需要注意的是，SwiftUI 的组件状态和行为都是由数据驱动，这可能会导致性能问题，如大量的数据绑定和更新可能会引起 UI 界面的卡顿和延迟。相比之下，UIKit 接近底层渲染机制，性能表现可能更佳。但 SwiftUI 也有实现跨平台需求的优势。

在选择具体哪个框架实现 Design System 时，开发者还是得根据具体需求，权衡两者之间的优缺点。在追求性能或需要高度定制化的场景下，UIKit 的灵活性和性能表现可能更占优。但在大多数情况下，SwiftUI 的声明式语法和组合特性，使其天然更适合构建统一且易维护的 Design System。
