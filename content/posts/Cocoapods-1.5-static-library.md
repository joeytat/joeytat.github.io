+++
title = "为什么 Cocoapods 1.5 支持编译静态库之后大家这么高兴?"
date = "2018-12-27"
tags = ["iOS"]
description = "昨天在 Twitter 上看到 TualatriX 说[把私有库都通过 Cocoapods 编译成静态库之后很爽](https://twitter.com/tualatrix/status/1077166131956264960), 就有点好奇到底是爽在哪里."
+++

昨天在 Twitter 上看到 TualatriX 说[把私有库都通过 Cocoapods 编译成静态库之后很爽](https://twitter.com/tualatrix/status/1077166131956264960), 就有点好奇到底是爽在哪里.

于是去搜了一下, 原来是前段时间(大半年前吧...), Cocoapods 发布了 1.5 的 [release note](http://blog.cocoapods.org/CocoaPods-1.5.0/), 宣布支持 Swift 静态库编译. 并且文中提到了对于担心动态二进制文件影响应用启动速度的人来说, 这是个了不起的更新.
jh
那又是为什么 App 使用静态库会比动态库有更快的启动速度呢? 又跑去搜了一下官方文档. 打开 [Dynamic Library Programming Topics](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/OverviewOfDynamicLibraries.html) 开头就看到:

> This article introduces dynamic libraries and shows how using dynamic libraries instead of static libraries reduces both the file size and initial memory footprint of the apps that use them. 

> 这篇文章主要介绍了动态库, 并且展示了通过**使用动态库**而不是静态库, 是如何**缩减**了应用的大小和初始内存空间的.

![黑人问号](http://ww1.rs.fanjian.net/c/ab/c8/25/53abf0c06ec808c1fe250d3565ff0d32.jpg)

┻━┻ (ヽ(`Д ́)ノ( ┻━┻  这和说好的不一样啊? 

带着疑问我又跑去看了一下苹果的 [WWDC 2016 -  Optimizing App Startup Time](https://developer.apple.com/videos/play/wwdc2016/406) 的视频, 这次问题终于得到了解决.

这里的库是什么? 是可执行文件的集合. 静态库与动态库调用时机的区别在于, 静态库在应用启动的时候, 会和程序的可执行代码一起, 被加载到应用的内存空间中. 这就会导致应用启动慢, 并且内存占用大. 而动态库则是在代码真正被需要调用的时候, 才加载到内存中. 

所以才会有苹果文档中提到的「通过**使用动态库**而不是静态库, 是如何**缩减**了应用的大小和初始内存空间的」这句话. 

可这是站在系统角度来说的. 在 iOS 中, 平均每个 App 包含了 [1 到 400](https://developer.apple.com/videos/play/wwdc2016-406/?time=1684) 个动态库. 其中有很大一部分是系统级动态库. 苹果为其做了许多的优化, 比如提前计算, 提前缓存等. 这对于系统提供的动态库来说, 当然比静态库更快.

但 App 中还包含了很多自有的动态库, 这部分动态库苹果没有办法为期提供优化. 而对于 dylib 的加载又是非常耗费资源的. 所以苹果对其的建议是最好在 [6](https://developer.apple.com/videos/play/wwdc2016-406/?time=1794) 个左右.

然后我也把项目中的 Swift pods 编译为静态库了, 效果如下.

```          
// 优化前
[DYMTLInitPlatform] platform initialization successful
Total pre-main time: 1.5 seconds (100.0%)
         dylib loading time: 968.07 milliseconds (61.1%)
        ......
        ......
```

```
// Pods 使用静态库后
[DYMTLInitPlatform] platform initialization successful
Total pre-main time: 1.1 seconds (100.0%)
         dylib loading time: 520.52 milliseconds (47.2%)
        ......
        ......
```

最后再总结一下. 

- 对于系统提供了优化的动态库来说, 一定是比静态库启动加载快且占用内存更小的. 14er
- 而对于 App 自有的动态库来说, 系统在加载动态库所消耗的资源要比加载静态库来得多, 所以最好限制在 6 个左右.

## 参考链接
- [Cocoapods 的静态库和动态库](https://www.jianshu.com/p/3d0ae289dee0)
- [WWDC 2016 - Optimizing App Startup Time](https://developer.apple.com/videos/play/wwdc2016/406/?time=203)
- [Dynamic Library Programming Topics](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/OverviewOfDynamicLibraries.html)
- [美团外卖 iOS App冷启动治理](https://tech.meituan.com/waimai_ios_optimizing_startup.html)