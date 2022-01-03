+++
title = "TIL - Platforms State of the Union(WWDC 2019)"
date = "2019-06-05"
author = "Joeytat"
tags = ["iOS"]
description = "观看 WWDC 2019 - Platforms State of the Union 的一些笔记"
+++

## SwiftUI 
在 View 层级提供了四种特性:
- Declarative
  通过声明式的语句来描述 UI 布局, 样式, 动画等.

- Automatic
  可交互形动画, 动态字号, 夜间模式都可以通过配置来轻松实现. 
  
- Compositional
  组合性. 各种控件都能极其方便地组合在一起, 远比 `UIStackView` 方便.
  
  ```swift
  VStack(alignment: .leading) {
      Text(item.title)
      Text(item.subtitle)
  }
  ```
- Consistent
  自带 Reactive 特性.  将 Model 对象继承自 `BindableObject`, 并且声明属性为 `@State` 即可获得当属性改变时, UI 控件自动更新的效果.
  
真的如果如此美好, 超级吃性能的 xib 和 storyboard 是不是可以退出舞台了.

## Xcode 11
- Live Development
  直接在 Xcode Preview 中拖动控件即可生成对应的 SwiftUI 代码. 对应的修改 SwiftUI 代码也能实时在 Preview 中响应.

  Preview 还能通过提供一个 `PreviewProvider` 来为其提供数据填充展示, 样式更改甚至循环语句来生成多个 Preview 同时查看控件在夜间模式和白日模式下不同的效果.

  Preview 部署在设备上也能热加载.

- Package Management
  Swift 终于有自己的 Package manage 了. 并且和 Xcode 进行了深度整合.
  
- Minimap
    代码在右侧会呈现类似 ctrl+6 的缩略图. 
    如果代码中写了 `// MARK: -` `// TODO: -` 等标记, 会更清晰地显示出来. 按住 cmd 会显示所有的标记.
    
- 版本管理
  可以直接在修改代码的位置查看到原来的版本.
  
- Test Plan
  同时测试各种平台各种设备.
  
## 跨平台方案
SwiftUI 支持跨平台,  同时支持 iOS, macOS, iPadOS. 那如何在 iOS App 的基础上创建一个 macOS App 呢? 只需要三个步骤: 
1. 勾选上 deployment 中的 ✅ mac   
2. 同时勾选上 ✅ iPad, 一个好的 iPad app, 就是一个好的 macOS app  
3. 针对 macOS 的菜单, 快捷键等具有平台特殊性质的操作进行一些单独适配.  

还对 catalina 的一些系统修改进行了介绍, 比如各种资源权限的收紧, 并且文件资源权限分成了两部分, 系统文件对于三方 app 变成了只读.

> 后面都是各平台系统或新功能的介绍, 还是不继续施工了. 