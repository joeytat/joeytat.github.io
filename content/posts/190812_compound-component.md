+++
title = "TIL - React 进阶模式之复合组件（Compound Component）"
date = "2019-08-12"
author = "Joeytat"
tags = ["React"]
description = "什么是复合组件，以及如何让子组件隐式地共享父组件的 props"
+++

### 复合组件是什么
编写页面时，经常存在多个子组件的展示，是依赖于同一个数据源的情况。
比如单选框：

```jsx
<Switcher>
    <Switch on={this.props.selecting == 'React'}>React</Switch>
    <Switch on={this.props.selecting == 'Vue'}>Vue</Switch>
</Switcher>
```

我们可以看到，所有的 `Switch` 的数据都需要对 `selecting` 的值进行判断，并且代码中其实只有 `this.props.selecting ==` 后面的部分不同，如果能改写成这样：

```jsx
static Switcher.React = ({selecting}) => (
  <Switch on={selecting === 'React'}>React</Switch>
)
static Switcher.Vue = ({selecting}) => (
  <Switch on={selecting === 'Vue'}>Vue</Switch>
)

<Switcher selecting={this.props.selecting}>
    <Switcher.React/>
    <Switcher.Vue/>
</Switcher>
```

隐式地将父组件的数据传递给子组件，其显示逻辑交由给子组件自行处理，代码的组织结构将会清晰很多。后续即使需求变动，数据的传递改变也并不需要我们操心（不需要一个子组件一个子组件地添加传递），只需要修改 `Switcher` 子控件内部处理逻辑即可。

那么要怎么实现这个**隐式数据传递**呢？ 可以通过 [`React.Children.map`](https://reactjs.org/docs/react-api.html#reactchildren) 和 [`React.cloneElement`](https://reactjs.org/docs/react-api.html#cloneelement) 这两个 API 来实现。

### React.Children.map 与 React.cloneElement
在 `render` 中我们可以使用  `React.Children.map` 来获取到 `Switcher` 中的子组件，然后通过 `React.cloneElement` 对组件进行克隆及数据传递：

```jsx
render() {
    return React.Children.map(this.props.children, child =>
      React.cloneElement(child, {
        on: this.state.on,
        toggle: this.toggle,
      }),
    )
  }
```

这样，即使我们在使用 `Switcher.React` 和 `Switcher.Vue` 时，没有显式地传递参数，子组件也能获取数据。

> 这里 `React.Children.map` 与 `this.props.children.map` 并不等价，后者在只有一个子组件的时候，返回的不是数组，而是唯一的那个组件。

### React.Children.map 的局限性
上面代码有个问题是，如果出现了更多层级的子组件，那么参数传递只会到第一层。

```jsx
<Switcher selecting={this.props.selecting}>
    <Switcher.React/>
    <div>
      <Switcher.Vue/>
    </div>
</Switcher>
```

这样写会提示传递了错误的参数给 `div`，因为我们 `React.Children.map` 只能获取到第一层子组件（`[Switcher.React, div]`）。

那怎么办，难道要用递归？React 16.x 提供了新的 [Context](https://reactjs.org/docs/context.html#when-to-use-context) 可以很好地解决这个问题。

Context 的使用方法很简单，首先创建一个 Context：

```jsx
const selecting = ""
const SwitcherContext = React.createContext("")
```

接着是 `render`，既然我们不确定会有多少层的子组件，那么就直接将 `this.props.children` 包裹在 `Context.Provider` 中：

```jsx
<SwitcherContext.Provider value={this.props.selecting}>
  {this.props.children}
</SwitcherContext.Provider>
```

然后改写我们的子组件数据获取方式，之前是通过 `React.cloneElement` 来将数据通过 `props` 传递到组件中，现在可以直接从 `Context.Consumer` 中获取：

```jsx
static Switcher.React =() => (
  <SwitcherContext.Consumer>
    { selecting => (
      <Switch on={selecting === 'React'}>React</Switch>) 
    }
  </SwitcherContext.Consumer>
)
```

如此一来就完成了我们的改造。外部使用到 `Switcher` 的地方没有任何变动，依然是：

```jsx
<Switcher selecting={this.props.selecting}>
    <Switcher.React/>
    <div>
      <Switcher.Vue/>
    </div>
</Switcher>
```

#### 相关资料
- [Frontend Masters - Advanced React Patterns](https://frontendmasters.com/courses/advanced-react-patterns/)
- [React Context](https://reactjs.org/docs/context.html#when-to-use-context)