+++
title = "TIL - JavaScript 既然是单线程语言，为什么 setTimeout 不会阻塞线程？"
date = "2019-08-19"
author = "Joeytat"
tags = ["JavaScript", "TIL"]
description = "一个问题简单地理解 Web Browser API，Callback Queue 与 Event Loop 是如何协作的"
+++

先看下面的代码

```javascript
function printHello() {
  console.log("Hello");
}
function printWorld() {
  console.log("World");
}
printHello(); // 输出 Hello
printWorld(); // 输出 World 
```

在 JavaScript 中，存在一个全局调用栈(Global Call Stack)。当我们调用 `printHello` 时，会将该方法加入到栈中，由于 JavaScript 是单线程执行机制（同一时间只执行一个命令），所以会在执行完成了 `printHello` 之后再执行 `printWorld`。

那么现在就引入标题中的问题，**JavaScript 既然是单线程语言，为什么 setTimeout 不会阻塞线程？**

```javascript
function printHello() {
  console.log("Hello");
}
function printWorld() {
  console.log("World");
}
setTimeout(printHello, 1000);
printWorld();
```

表面上来看 `setTimeout` 也是一个方法，他的定义可能是这样：

```javascript
function setTimeout(callbackFunc, interval) {
  // ....
}
```
那么按照 JS 单线程理论来说，应该是先将 `setTimeout` 方法压入全局调用栈，并且执行该方法，等待 1 秒钟，然后再执行 `printWorld` 才对。但实际上我们都知道，打印的结果会是 "World" 然后 "Hello"，这是为什么？

### Web Browser API &  Callback Queue
事实上 `setTimeout` 并不是完全是 JS  代码，而是属于 **Web Browser API** 中的方法。就像名字中所指的那样， JS 调用了 `setTimeout` 之后，浏览器（Web Browser）会去创建一个 timer，同时将我们传入 `setTimeout` 的方法 - `printHello` 加入到 **Callback Queue（回调队列）** 中。

1000 毫秒过去后，浏览器会通知 JavaScript 引擎将回调队列中的 `printHello` 加入到 JS 的全局调用栈中执行。

所以在 JS 的全局调用栈看来，是先有一个 `printWorld` 加入到了调用栈，过了 1000 毫秒之后，又加入了一个 `printHello` 方法。

那如果我们的 `printWorld` 之后还有其他的方法执行时间超过了 1000 毫秒呢？

```javascript
/// 省略掉 printHello 和 printWorld 定义

function heavyWork() {
    for(let i = 0; i < 1000000; i++) {
      console.log("Heavy Work"); 
    }
}

setTimeout(printHello, 1000);
printWorld();
heavyWork(); // 假设会执行 2000ms
```

现在让我们假设 `heavyWork` 方法会执行 2000ms，可是我们的 `setTimeout` 只会执行 1000ms，那么按照上面的理论，1000ms 到了之后，`printHello` 会被加入到 JS 的调用栈中执行，那现在的输出会是一堆“Heavy Work”之中夹带着一个“Hello”吗？

```javascript
World
Heavy Work
...
Hello // 会输出一堆 Heavy Work 中夹带一个 Hello 吗？
...
Heavy Work
```

当然不会啦，因为我们有 Event Loop（事件循环机制）。

### Event Loop
Event Loop 其实理解起来非常简单，就是一个循环会不停地检查 JS 调用栈。只有在 JS 调用栈**没有任务**的情况下，Callback Queue 中的任务，才会被添加到 JS 调用栈。

所以上面的代码中，`setTimeout` 虽然指定了 1000ms 之后就执行 `printHello`，但实际上会被需要执行 2000ms 的 `heavyWork`阻塞住， 输出的结果会是：

```javascript
World
Heavy Work
.... // 长达 2000ms 的 Heavy Work
Heavy Work
Hello
```

### 总结
- Web Browser API  
  提供给我们 JavaScript 所没有后台运行任务的能力，除了 `setTimeout` 和 `setInterval` 这样创建 timer 的 API 之外，还包括了 Ajax，用户交互，文件读写等操作。
- Callback Queue  
  用于持有提交到 Web Browser API 中等待回调的 callback。
- Event Loop  
  一个不停地检查 JavaScript 调用栈中是否还有任务的循环。