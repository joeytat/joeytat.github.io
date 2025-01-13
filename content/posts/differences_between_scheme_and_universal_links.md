+++
title = "移动开发中实现 Deep Linking 的 URL Scheme 和 Universal Links 的区别是什么？"
date = "2022-07-27T00:00:00"
tags = ["KnownEnoughToBeDangerous"]
description = "经历过的 Mobile 项目基本上都有支持 Deep Linking 的需求，每次新项目都会经历向其他端同事和 BA 解释实现 Deep Linking 两种方案的区别，于是就有了这一篇短文。主要是介绍两种方案的优缺点和实现成本差异，并不涉及如何实现的代码步骤。"
+++

经历过的 Mobile 项目基本上都有支持 Deep Linking 的需求，每次新项目都会经历向其他端同事和 BA 解释实现 Deep Linking 两种方案的区别，于是就有了这一篇短文。主要是介绍两种方案的优缺点和实现成本差异，并不涉及如何实现的代码步骤。

首先什么是 Deep Linking，简单来说就是让一个 App 可以通过 URL 打开其他的 App，以提供更便捷高效的用户体验。

## 如果想跳到别人那去
BA 老刘：「如果想在 App 里打开人家的 App 应该怎么做呢？」  
开发小曾：「目前有两种选项，URL Scheme 和 Universal Links。」  
BA 老刘：「区别是啥？」  
开发小曾：「主要看你想不想处理用户没有安装对方 App 的情况。」  

*ps: Android 中这两种选项是 Deep Links 和 App Links，运作原理大体相同，实现方式 iOS 和 Android 有些许差异。为少打字，下文将统一使用 URL Scheme 和 Universal Links。*

### URL Scheme
通常长这样： `example://destination?param1=hello`。

想通过 URL Scheme 跳转到某个 App，我们需要知道对方 App 定义的 Scheme 是什么（这不算是废话）。

以 Twitter 为例，如果当前设备**安装了 Twitter**：  
通过 `twitter://user?screen_name=elonmusk` 这样一个 URL Scheme，就可以打开 Twitter 并且跳转到 Elon Musk 的主页（scheme 可以输入 Safari 地址栏进行测试）。

如果当前设备**没有安装 Twitter**：  
可以通过代码得到无法解析 URL 的错误，接下来要如何处理，就需要工程师自己去实现了。
比如可以加上判断，如果打不开 Twitter 的 Scheme，就去打开 App Store 的 Scheme 引导用户下载 Twitter，或者去打开微博。

### Universal Links
Universal Links 则是使用了 HTTP 或 HTTPS（iOS 只支持 HTTPS）Scheme 的 URL。

依然用 Twitter 举例：  

如果当前设备**安装了 Twitter**：  
通过打开 URL `https://twitter.com/elonmusk` 可以跳转到 Twitter App 中 Elon Musk 的主页。

如果用户**没有安装 Twitter**：  
会打开网页版 Elon Musk 的主页。

### 方案对比

|  | 有安装对应 App | 没有安装对应 App |
| ---- | ---- | ---- |
| URL Scheme | 直接打开对应 App | 需要自行处理设备没有安装对应 App 的情况，但处理方案可以非常灵活多变 |
| Universal Links | 直接打开对应 App | 无需额外处理，通常 Universal Link 就对应了一个网页，在当前设备没有安装 App 的情况下，会跳转到对应网页 |

## 如果想让别人跳过来
BA 老刘：「那如果想让我们的 App 支持跳转呢？」。  
开发小曾：「还是那两种选项，URL Scheme 和 Universal Links。」  
BA 老刘：「区别是啥？」  
开发小曾：「主要是实现成本和想支持跳转的范围。」  

### URL Scheme
在 App 中设置一个自定义 Scheme 即可。当三方 App 通过代码调用尝试跳转某个 Scheme，系统会检测当前设备是否安装了有定义该 Scheme 的 App。

如果想要支持对方跳转到某个特定界面，只需要在 App 中增加解析 URL 的方法即可。
具体实现细节可以参考：
- [iOS - Defining a custom URL scheme for your app](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app)
- [Android - Hanling Android App Link - Deep Links](https://developer.android.com/training/app-links#deep-links)

### Universal Links
相比起 URL Scheme 只需要前端实现，Universal Links 的支持要复杂一些，原因是在于其使用场景扩大了。  
URL Scheme 的跳转，需要让三方 App 知道我们的 Scheme 定义即可，由**第三方 App 来发起跳转**。如果当前设备并没有安装 App，如何提供备选方案，就完全依赖于三方实现了。

Universal Links 的跳转，是三方 App 打开一个链接时，由系统决定应该跳转到 App（将其当作 Universal Link） 还是跳转到网页（将其当作普通的 HTTP Link）。同时系统来控制跳转，则意味着用户从系统中几乎任何地方（比如邮件、短信、备忘录、日历）点击 Universal Link 都能跳转到 App 中。这样即使在当前设备没有安装 App 的情况下，依然保证用户可以通过网页访问到需要的资源。

所以实现的区别在于，需要让系统知道，哪些域名的 URL 是应该跳转到我们的 App。

依然用 Twitter 举例，当我们需要让系统支持在点击任何带有 `twitter.com` 为 Host 的链接时，都尝试着唤起 Twitter 就需要：
1. 开发人员需要在 Twitter App 的配置中，添加 associated domain 的记录，比如 `twitter.com`。
2. 当 Twitter App 被安装到用户的手机或者应用更新时，系统会去 Twitter App 包中查找 associated domain 记录。
3. 如果存在这样一份记录，系统会去访问该 domain 下的一个 JSON 文件，该文件中需要包含 Twitter App 的 App ID，以建立该站点与 App 的联系。比如 Twitter 就将这份 JSON 文件放在了  `https://twitter.com/.well-known/apple-app-site-association`。
4. 由此当系统在处理链接的点击时，会去判断 `https://twitter.com` 是否和当前设备中安装的某个 App 之间存在联系，如果已安装的某个 App 的 app id 存在于该 domain 下的 site association JSON 文件中，则将 URL 作为参数代入，跳转到 App 中。

用图片来表示的话，大概是这样，首先让 OS 建立域名和 App 的联系：

![make connection between domain and the app](/deeplinking_connection.png)

当存在联系之后，点击链接时，OS 会去唤起 App：

![tapping on the link will navigate to the app](/deeplinking_connection1.png)

具体实现细节可以参考：
- [iOS - Allowing Apps and Websites to Link to Your Content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Android - Hanling Android App Link](https://developer.android.com/training/app-links#android-app-links)

### 对比
|  | 实现成本 | 支持跳转的范围 | 没有安装 App |
| ---- | ---- | ---- | ---- |
| URL Scheme | 需要在 App 中维护一个支持被跳转的 Scheme 列表 | 只能由知道 Scheme 的 App 来主动进行跳转 | 需要让三方 App 来处理没有安装 App 的情况 |
| Universal Links | App 中要维护一个支持被跳转的 domain 列表，同时需要在 domain 对应服务器中放一个 JSON 文件，让系统知道该 domain 同 App 之间的联系 | 系统中几乎所有可点击链接区域都可以被系统触发跳转，比如点击邮件、短信、网页、三方 App 中的 Universal Link 时 | 用户会跳转到 Universal Link 对应的网页，在网页中我们可以实现一套 Web 版本，或者直接在网页中打开应用商店，引导用户下载 App |

## 简单总结
跳到别人那去，一般来说在需要灵活处理当前设备**没有安装**对方 App 的情况下，通常会选择 URL Scheme，否则选择 Universal Links。

支持别人跳过来，两个方案可以共存。
- URL Scheme 相对来说实现成本非常低廉，仅需要前端维护 Scheme 列表并且负责解析即可。但需要让对方来处理，如果当前设备没有安装 App 应该怎么办。
- Universal Links 的实现则相对复杂，必须要把 domain 和 app 之间建立联系的 json 文件放在服务器，让系统在安装 App 的时候去访问。但好处是，如果本来就有 Web 版的业务，那么自动就可以在用户未安装 App 时得到相应的服务。