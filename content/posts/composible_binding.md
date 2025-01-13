+++
title = "SwiftUI 状态管理 —— Composible Binding"
date = "2022-01-03"
description = "如何利用 Enum 以及自定义 KeyPath 来更好地管理 SwiftUI 的状态"
tags = ["SwiftUI"]
+++
在 SwiftUI 中，需要通过数据来驱动 UI 的变化。数据结构抽象描述的质量也影响着我们对 SwiftUI 界面的维护。

通常数据中可能存在很多状态，如果使用很多的 boolean 值来描述这些状态，那么 App 的可维护性可能会大大降低。

## 管理独立状态的问题
假设我们有一个 App，用户可以在登录与非登录状态下进行操作。所以我们的界面需要兼容这两种状态，其描述可能是这样的：
```swift
class AppState: ObservableObject {
  @Published var user: User? = nil
  @Published var error: Error? = nil
  
  var authenticated: Bool { user != nil }
  var hasError: Bool { error != nil }
}
```
基于这样的状态描述，如果我们想创建一个仅展示用户名的组件大概会是这样：
```swift
  var body: some View {
    Group {
      if state.hasError {
        Text("Oops, sth went wrong: \(state.error!.localizedDescription)")
      }
      if state.authenticated {
        Text("Hello \(state.user?.name ?? "Unknown")!")
      } else {
        Text("Hello, stranger")
      }
    }
  }
```
粗看没有什么问题，实际上在维护这样的数据结构时就需要格外小心了。比如第一次我们登录失败，为了展示错误信息给 `error` 设置了值之后。必须在登录成功之后要及时地去清空 error，否则即使 `state.authenticated` 等于 `true`，用户依然无法看到正确的信息。

这还仅仅是有两个状态的情况下，像这样独立状态属性会带来很大的维护成本，开发者需要牢记各个属性之间的依赖关系，甚至编写界面的时候，还需要注意代码执行顺序。

## 引入状态机
把状态抽象成带有 associated values 的 enum 是个更好的选择，比如:
```swift
class AppState: ObservableObject  {
  enum AccountState {
    case authenticated(User)
    case unauthenticated
    case error(Error)
  }
  @Published var accountState: AccountState = .unauthenticated
}

// 界面中的使用
var body: some View {
  VStack {
    switch state.accountState {
    case .authenticated(let user):
      Text("Hello \(user.name)!")
    case .unauthenticated:
      Text("unregister")
    case .error(let error):
      Text("Oops, sth went wrong: \(error.localizedDescription)")
    }
}
```
这样被状态机驱动的界面看起来要直观多了。并且在每个状态中对数据的操作，也由 enum 赋予了隔离能力。

##  双向绑定怎么办？
但这样做又来带个新的问题，现在没办法直接通过 `$` 来获取 Binding wrapper 来修改状态：
```swift
switch state.accountState {
    case .authenticated(let user):
      Text("Hello \(user.name)!")
	  TextField("Change username", text: <Binding<String>>) 
      // 不支持填入 self.$state.accountState.name 👆
	...
```

> Xcode 会提示: dynamic member 'name' using key path from root type 'AppState.AccountState'

为什么当操作对象是 class 时，是可以做到通过 
`self.$state.user.name` 来获取到 name 属性的 Binding 封装的？

## 实现动态成员查找(dynamic member lookup)
因为 Enum 还不支持动态成员查找特性。什么是动态成员查找？简而言之就是通过  `\` 来获取到成员属性的 `KeyPath` 封装（[什么又是 KeyPath](https://www.swiftbysundell.com/articles/the-power-of-key-paths-in-swift/)？），然后将其转化为对应的 Binding 封装。
```swift
extension Binding {
  func transform<LocalValue>(
    _ keyPath: WritableKeyPath<Value, LocalValue>
  ) -> Binding<LocalValue> {
    Binding<LocalValue>(
      get: { 
        self.wrappedValue[keyPath: keyPath]
      },
      set: { localValue in
        self.wrappedValue[keyPath: keyPath] = localValue 
      }
    )
  }
}

self.$state.accountState.username
// 等价于 
self.$state.transform(\accountState).transform(\username)
```
所以接下来只需要为 enum 添加动态成员查找的支持就可以了
```swift
extension Binding {
  func unwrap<Wrapped>() -> Binding<Wrapped>? where Value == Wrapped? {
    guard let value = self.wrappedValue else { return nil }
    return Binding<Wrapped>(
      get: { value },
      set: { self.wrappedValue = $0 }
    )
  }
}
```
然后再到 enum 里添加一个计算属性方便我们获取
```swift
enum AccountState {
  case loggedIn(User)
  case unregister
  //
  var username: String? {
    get {
      guard case .loggedIn(let user) = self else {
        return nil
      }
      return user.username
    }
    set {
      guard case .loggedIn(let user) = self,
            let newValue = newValue else { return }
      user.username = newValue
      self = .loggedIn(user)
    }
  }
}
```
现在就可以在 SwiftUI 中对 enum 使用绑定了
```swift
if let username = self.$state.accountState.username.unwrap() {
  TextField("Change username", text: username)
}
```
看起来还是有些麻烦，对于每个要使用 Binding 的属性都需要去写一个计算属性来包装一层。这样显然这并不如 `KeyPath` 那样，直接通过 `self.$state.accountState[\.authenticated]` 来获取到 enum 中 associated value 的 Binding 包装来得方便。

虽然 Swift 目前不支持，但我们还是可以通过引入 [CasePaths](https://github.com/pointfreeco/swift-case-paths) 这个第三方依赖来实现。

```swift
import CasePaths

enum AccountState {
  case authenticated(User)
  case unauthenticated
  case error(Error)
// 计算属性可以删除掉了
//    var username: String? {
//      get {
//        guard case .authenticated(let user) = self else {
//          return nil
//        }
//        return user.name
//      }
//      set {
//        guard case .authenticated(let user) = self,
//              let newValue = newValue else { return }
//        user.name = newValue
//        self = .authenticated(user)
//      }
//    }
}

// 界面中直接使用 CasePath
if let user = self.$state.accountState.matching(/.authenticated) {
  TextField("Change username", text: user.name)
}

```

由此为 Enum 也增加了与 Struct、Class 等效的 KeyPath 支持，从而使得文章开头用 Enum 作为 SwiftUI 的状态机管理工具更便捷了一些。

## 参考资料
- [Stop using isLoading booleans](https://kentcdodds.com/blog/stop-using-isloading-booleans)
- [The power of key paths in Swift](https://www.swiftbysundell.com/articles/the-power-of-key-paths-in-swift/)
- [Composable SwiftUI Bindings: The Problem](https://www.pointfree.co/collections/swiftui/composable-bindings/ep107-composable-swiftui-bindings-the-problem)