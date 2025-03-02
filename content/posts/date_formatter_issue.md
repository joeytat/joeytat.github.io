+++
title = "DateFormatter 静态实例的一个小坑"
date = "2025-03-02"
tags = ["swift"]
+++

## 问题

目前开发的 app 主要服务于澳洲用户，开发团队由中澳两地开发人员组成，所以写和 DateFormatter 相关测试时，通常会指定 Calendar 所处时区。否则可能出现测试在本地运行完美通过，但澳洲同事本地或者 CI 上挂掉的情况出现。

```swift
var mockCalendar = Calendar(identifier: .iso8601)
let mockDate = mockCalendar.date(
  from: DateComponents(year: 2025, month: 3, day: 2, hour: 12)
)!
// 如果跑测试时候的时区是 Australia/Sydney，那么生成的日期是 02 Mar 09:00
#expect(humanizedDate(date: mockDate) == "02 Mar 12:00”) // ❌
```

要解决这个问题，通过指定 Calendar 及 DateFormatter 的时区为同一时区即可。

```diff
var mockCalendar = Calendar(identifier: .iso8601)
+ mockCalendar.timeZone = TimeZone(identifier: "Australia/Sydney")!

let formatter = DateFormatter()
+ formatter.dateFormat.timeZone = mockCalendar.timeZone

let mockDate = mockCalendar.date(
  from: DateComponents(year: 2025, month: 3, day: 2, hour: 12)
)!
#expect(humanizedDate(date: mockDate, formatter: formatter) == "02 Mar 12:00”) // ✅
```

## 优化

但在生产代码中考虑到 DateFormatter 在使用的时候如果不重用实例，则会额外耗费十几倍的时间。
![how-expensive-is-dateformatter-when-using](/date-formatter-time-consuming.png)

ref：[how-expensive-is-dateformatter-when-using](https://sarunw.com/posts/how-expensive-is-dateformatter/#experiment-%232%3A-how-expensive-is-dateformatter-when-using)

所以我们的做法是将 DateFormatter 的实例以静态变量的方式存储起来。

```swift
extension DateFormatter {
  static let ddMMMHH: DateFormatter = {
  let formatter = DateFormatter()
  formatter.dateFormat = "dd MMM HH"
  return formatter
  }()
}
```

这样直接每次需要用到 dd MMM HH 这个格式的 formatter 时就不需要重复创建实例。

## 测试崩溃

一切都挺好，直到项目的单元测试开始使用 [Swift Testing](https://developer.apple.com/xcode/swift-testing/)。比较古怪的事情发生了，这些用 Swift Testing 新写的与 date formatter 相关的测试开始崩溃。每一个单独运行都能通过，但只要一起运行就开始崩溃 `Test crashed with signal segv`。

一番查找之后发现原因在于 Swift Testing 默认情况下是并行运行的，但 DateFormatter 并不是线程安全的。当多个测试同时修改静态 DateFormatter 的 timeZone 属性时，可能会触发线程安全问题，导致段错误（segv）。Swift Testing 的并行特性放大了并发修改的频率，问题就暴露出来了。

权衡了一下，通过在测试中隔离 DateFormatter 实例，将 DateFormatter 作为参数传入方法，在测试中为每个用例创建独立的实例，生产环境依然使用共享实例的方案来解决问题。
