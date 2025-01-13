+++
title = "如何实现 JavaScript 函数参数必填的支持?"
date = "2019-06-03"
tags = ["JavaScript"]
+++

JS 在 ES6 的中新增了函数参数指定默认值的支持:

```js
const Greeting = (name="Joeytat") => {
  console.log(`Hello ${name}`)
}
Greeting() // Hello Joeytat
```

那我们就可以利用这一特性, 将一个会抛出异常的方法作为默认参数传递. 

```js
const Greeting = (name=EmptyPropertyException("name")) => {
  console.log(`Hello ${name}`)
}

const EmptyPropertyException = (propertyName) => {
  throw Error(`${propertyName} 为必填参数`)
}

Greeting() // 抛出异常: "Error: name 为必填参数"
```

这样如果没有传递参数就会抛出异常, 并且带有友好的提示了.
