+++
title = "Swift 状态管理 —— 如何拆分庞大的 reducer"
date = "2022-01-16"
description = "利用 keyPath 构建 pullback 来处理 reducer 状态隔离的问题"
tags = [""]
+++

因为项目需要使用 SwiftUI，想起来之前买过喵神的 [《SwiftUI 与 Combine 编程》](https://objccn.io/products/swift-ui) 。书中介绍了 [Redux](https://redux.js.org) 这一在 Web 前端领域广泛被验证过的数据管理模式是如何通过 Swift 来实现的，非常推荐 SwiftUI 初见者阅读。

在学习过程中还产生了一个疑问，如果 reducer 越来越大，有什么更  “swift” 的办法能解决这一问题呢？（在 Redux.js 中的原生解决方案是 [`combineReducers`](https://redux.js.org/usage/structuring-reducers/beyond-combinereducers)）

## 拆分 Reducer
首先看看问题在代码中的表现是什么样的，假设我们有这样一个 reducer：

```swift
func appReducer(appState: inout AppState, action: AppAction) -> Void {
    switch action {
    case .emailValid(let isValid):
        appState.settings.isEmailValid = isValid
        
    case .register(let email, let password):
        appState.settings.loginUser = User(email, password)
    
    case .login(let email, let password):
        appState.settings.loginUser = User(email, password)
    
    case .logout:
        appState.settings.loginUser = nil
        
    case .loadPokemon(let result):
        appState.pokemonList.pokemons = result
        
    case .favoratePokemon(let pokemon):
        appState.favoritePokemons.append(pokemon)
        
    case .removeFavoritePokemon(let pokemon):
        let index = appState.favoritePokemons.indexOf(pokemon)
        appState.favoritePokemons.remove(at: index)
}
```

应用的 action 主要包含三个模块：
- 账号登录注册注销
- 对神奇宝贝数据进行加载
- 处理对神奇宝贝数据的收藏和取消收藏

从这段代码我们很快就能发现，即使只是非常简单的示例也已经包含了不短的代码了。这里还省略掉了处理状态时可能还需要的异步 action 的处理（数据加载等）。这还仅仅只有两个非常简单的界面状态，当面对真实的 app 所需要处理的数十个页面状态会更恐怖。

将 reducer 拆分成如下三个独立 reducer：

```swift
func accountReducer(appState: inout AppState, action: AppAction) -> Void {
    switch action {
    case .emailValid(let isValid):
        appState.settings.isEmailValid = isValid
        
    case .register(let email, let password):
        appState.settings.loginUser = User(email, password)
    
    case .login(let email, let password):
        appState.settings.loginUser = User(email, password)
    
    case .logout:
        appState.settings.loginUser = nil

    default:
        break
}

func pokemonListReducer(appState: inout AppState, action: AppAction) -> Void {
    switch action {
    case .loadPokemon(let result):
        appState.pokemonList.pokemons = result

    default:
        break
}
    

func favoritePokemonReducer(appState: inout AppState, action: AppAction) -> Void {
    switch action {
    case .favoratePokemon(let pokemon):
        appState.favoritePokemons.append(pokemon)
        
    case .removeFavoritePokemon(let pokemon):
        let index = appState.favoritePokemons.indexOf(pokemon)
        appState.favoritePokemons.remove(at: index)

    default:
        break
}
   
```

因为对 reducer 的数量并不确定，所以这里使用可变参数来构建 `combine` 方法，对传入的 reducer 进行遍历调用处理 appState。

```swift
func combine<Value, Action>(
  _ reducers: (inout Value, Action) -> Void...
) -> (inout Value, Action) -> Void {
  return { value, action in
    for reducer in reducers {
      reducer(&value, action)
    }
  }
}

let appReducer = combine(
  accountReducer,
  pokemonListReducer,
  favoritePokemonReducer
)
```

完成，我们的巨大 reducer 被拆分成了独立的 reducer，再通过自己实现的 combine 方法完成了组装。

## 隔离 reducer 数据

但仔细观看代码还会发现一个问题，每个 reducer 都只需要处理 `appState` 上的部分数据，比如 `pokemonListReducer` 明明只操作了 `appState.pokemonList`，我们却把整个 state 都丢给了它：

```swift
func pokemonListReducer(appState: inout AppState, action: AppAction) -> Void {
    switch action {
    case .loadPokemon(let result):
        appState.pokemonList.pokemons = result

    default:
        break
}
```

这会增加代码维护上的困难，不熟悉代码的人在不浏览整个 reducer 之前，很难知道这个 reducer 到底操作了哪些数据。更理想的 reducer 可能长这样：

```swift
func pokemonListReducer(value: inout PokemonList, action: AppAction) -> Void {
    switch action {
    case .loadPokemon(let result):
        value.pokemons = result // 👈  只能操作 pokemonList

    default:
        break
}
```

只是这样改动之后，之前定义的 combine 就无法编译通过，pokemonListReducer 的签名已经不符合 combine 的要求了。

> Cannot convert value of type ‘(inout PokemonList, AppAction) -> ()’ to expected argument

### 拉回
解决这个问题可以引入一个数学中的概念 —— 拉回。

> 引用 wikipedia 上的解释：“简单地说，设 _f_ 是一个变量 _y_ 的函数，这里 _y_ 自身又是另一个变量 _x_ 的函数，那么 _f_ 可以写成 _x_ 的函数，这即 _f_ 被函数 _y_(_x_) 拉回。”

在 reducer 中的例子里，也可以套用相同的概念。只需要将持有了部分状态数据的 reducer，转化成一个拥有着全部状态数据的 reducer 签名即可：

```swift
func pullback<LocalValue, GlobalValue, Action>(
  _ reducer: @escaping (inout LocalValue, Action) -> Void,
  get: @escaping (GlobalValue) -> LocalValue,
  set: @escaping (inout GlobalValue, LocalValue) -> Void
) -> (inout GlobalValue, Action) -> Void {

  return  { globalValue, action in
    var localValue = get(globalValue)
    reducer(&localValue, action)
    set(&globalValue, localValue)
  }
}
```

该函数包含三个入参：
1. 用于处理局部状态的 reducer
2. 提供从全部状态中提取部分状态的函数
3. 提供将局部状态设置到全部状态中的函数

这样就得到了一个可以用来转化用于处理局部状态 reducer 到全部状态 reducer 的 pullback 函数：
```swift
pullback(pokemonListReducer,
         get: { $0.pokemonList },
         set: { $0.pokemonList = $1 }
         )
```

再进一步还可以通过 keyPath 来优化 pullback 函数：

```swift
func pullback<LocalValue, GlobalValue, Action>(
  _ reducer: @escaping (inout LocalValue, Action) -> Void,
  value: WritableKeyPath<GlobalValue, LocalValue>
) -> (inout GlobalValue, Action) -> Void {
  return { globalValue, action in
    reducer(&globalValue[keyPath: value], action)
  }
}

      
pullback(pokemonListReducer, value: \AppState.pokemonList)
```

这样就实现了 reducer 的拆分以及对处理状态的隔离

```swift
let appReducer = combine(
  pullback(accountReducer, value: \.pokemonList),
  pullback(pokemonListReducer, value: \.settings),
  pullback(favoritePokemonReducer, value: \.favoritePokemons)
)
```

## 参考资料
- [ObjC 中国 - SwiftUI 与 Combine 编程](https://objccn.io/products/swift-ui)
- [Point Free - State Pullbacks](https://www.pointfree.co/collections/composable-architecture/reducers-and-stores/ep69-composable-state-management-state-pullbacks#downloads)
- [Swift by Sundell - The power of key paths in Swift](https://www.swiftbysundell.com/articles/the-power-of-key-paths-in-swift/)