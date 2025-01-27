+++
title = "翻译 - 图像优化"
date = "2019-06-19"
tags = ["iOS", "翻译"]
description = "(通过啦～✌️)  发现 SwiftGG 在招人, 需要试译一篇文章. 花了半个下午加上午的时间来翻译, 于是就有了这篇. 不知道能不能通过."
+++

翻译自 [Optimizing Images](https://www.swiftjectivec.com/optimizing-images/) by [Jordan Morgan](https://twitter.com/jordanmorgan10)

有句话说：最好的照相机就是在你身边的那台。 如果这句俗语是对的，那么毫无疑问地— iPhone 是这个星球上最重要的相机， 并且我们的业界也证明了这一点。

在度假中? 如果没有在你的 Instagram Story 中留下几张照片，那就不算发生过。

爆炸新闻?  立刻打开 Twitter 来查看哪些媒体在通过照片实时报道事件。

等等。

由于图像在各个平台无处不在的出现，在低性能且内存紧张的情况下展示它们，会很容易地造成失控。 如果我们知道 UIKit 底层到底发生了什么，为什么以及如何处理图像，那么我们可以节省大量的资源开销，并且逃脱无情的系统清除制裁。

## 理论上来说

突击测验 - 这张我女儿的 266 KB 字节大小（并且还蛮时尚的）的照片，在一个 iOS App 中会展示需要用到多少内存? 

![Baylor](https://www.swiftjectivec.com/assets/images/baylor.jpg)

剧透一下 - 不是 266 KB，也不是 2.66 MB，而是大概 14 MB。

为什么? 

本质上来说 iOS 申请内存是根据图像的尺寸 - 而图像的文件大小反而影响不大。 这张图片的尺寸是 1718 x 2048 像素。 假设每个像素会占用 4 个字节: 

> 1718 * 2048 * 4 / 1024 / 1024 = 13.42 MB  大约

想象一下，如果你需要展示一个列表的用户信息，其中每一行都显示一个常见的圆形头像在左侧。 如果你觉得每一张图片都通过 ImageOptim 或者其他方式处理过就没问题，那就错了。 保守估计每一张头像是 256 x 256 大小，那依然会耗费大量内存。

## 渲染路径
这就是说 - 明白底层是怎么回事是很划算的。 当你加载一张图片的时候，会经由这三步处理: 

1） 加载 - iOS 会获取到尚未解压的图片，然后开辟（我们的图片举例） 266 kb 的内存，目前为止没什么好担心的。 

2） 解码 - 现在 iOS 会将图片转化为 GPU 可以读取并且处理的数据。 现在是解压，在这一步就会产生我们上面提到的 14 MB 的内存开销。

3） 渲染 - 按照字面意思理解，现在图片数据准备好了以任何方式进行渲染。 即使是放在 60 x 60 point 的 image view 中。

解码阶段是大头。 在这里 iOS 会创建一个缓冲区 - 准确的说是图片缓冲区。 这里会将图像放在内存中。 这也是为什么，其内存占用会和图片尺寸挂钩而不是图片文件大小。 这就清晰地解释了，当处理图片时，为什么尺寸对于内存消耗如此重要。 

针对 `UIImage`， 当我们把从网络请求或者其他途径获取的图片数据传递给它时，它会将缓冲区的数据解码成数据声称的格式（比如 PNG 或者 JPEG）。 然而它就会在这停顿了。 由于渲染并非只是一次性操作，`UIImage` 会保留这个数据缓冲，这样它只需要解码一次。 

我们来扩展一下这个概念 - 对于任何 iOS App 来说一个完整的缓冲区就是其帧缓冲区。 这就是当 app 展示在屏幕上时，负责持有输出渲染内容的东西。 任何 iOS 设备上的显示硬件，都会使用其中的像素信息来点亮对应的物理屏幕像素。

此处时间很重要。 为了达到每秒 60 帧如黄油般顺滑的滚动效果，在 app 的 window 及其 subviews 改变的时候（比如分配了一个 image 给 image view），帧缓冲区需要 UIKit 来渲染。 如果渲染慢了，就会掉帧。

> 觉得只有 1/60 秒处理时间太短了? 具备 Pro Motion 的设备只会给 1/120 秒的时间。

## 大小真的很重要
我们其实可以很轻松地观察到这步处理以及内存时如何被消耗掉的。 我创建了一个实验 app，用 image view 来展示了我女儿的照片。

```swift
let filePath = Bundle.main.path(forResource:"baylor"，ofType: "jpg")!
let url = NSURL(fileURLWithPath: filePath)
let fileImage = UIImage(contentsOfFile: filePath)

// Image view
let imageView = UIImageView(image: fileImage)
imageView.translatesAutoresizingMaskIntoConstraints = false
imageView.contentMode = .scaleAspectFit
imageView.widthAnchor.constraint(equalToConstant: 300).isActive = true
imageView.heightAnchor.constraint(equalToConstant: 400).isActive = true

view.addSubview(imageView)
imageView.centerXAnchor.constraint(equalTo: view.centerXAnchor).isActive = true
imageView.centerYAnchor.constraint(equalTo: view.centerYAnchor).isActive = true
```

> 这里我们只是为了演示场景，在生产环境中请谨慎使用强制解包。

上面的代码运行起来时这样: 

![Baylor](https://www.swiftjectivec.com/assets/images/baylorPhone.jpg)

虽然我们使用了一个小得多的 Image View 来展示图片，但通过 LLDB 我们可以查看到图片实际的尺寸。

```swift
<UIImage: 0x600003d41a40>，{1718，2048}
```
记住，这是点表示。 所以如果我使用的是 3x 或者 2x 设备，这个数字需要更大一些。  我们可以使用 vmmap 来确定这张图片是否真的占用了 14 MB。

```
vmmap --summary baylor.memgraph
```

有几个东西引起了注意（为了简洁只截出了部分输出）: 

```
Physical footprint:         69.5M
Physical footprint (peak):  69.7M
```

接近 70 MB 给了我们一个很好的参考来确定我们的重构是否有效。 如果我们通过 grep 命令来筛选 Image IO，我们也能够看到图片的开销。

```
vmmap --summary baylor.memgraph | grep "Image IO"

Image IO  13.4M   13.4M   13.4M    0K  0K  0K   0K  2 
```

啊哈 - 这里就有接近 14 MB 的脏内存。 如同我们在餐巾纸背面写下的公式计算的那样。 背景补充一下，这是一个终端的屏幕截图，清楚地显示了每一列的含义。 （由于他们被 grep 命令给省略掉了）

![](https://www.swiftjectivec.com/assets/images/vmmap.jpg)

所以很明确了，此刻我们在 300 x 400 的 image view 中也依然付出了图像的完整开销。 图像的大小是很关键，但这并不是唯一重要的点。

## 色域
你所请求的内存消耗有一部分源于另一个重要因素 - 色域。 在上面的例子中我们做了一个假设，而这个假设并不适用于大多数 iPhone - 也就是图像采用的是 sRGB 格式。 每个像素 4 个字节对应的是红，蓝，绿以及透明。

如果你使用的是支持广色域格式的设备（iPhone 8+ 或 iPhone X）进行拍摄，那就可以肯定数字会加倍了。 当然了，反过来也一样，Metal 支持使用 Alpha 8 格式，就像其名字描述的那样只有单一通道。

这里有非常多需要考虑的东西。 这也是为什么你应该使用 [UIGraphicsImageRenderer](https://swiftjectivec.com/UIGraphicsImageRenderer) 而不是 `UIGraphicsBeginImageContextWithOptions`。 后者会**一直**使用 sRGB，这也意味着你会丢失广色域格式，如果你 [想要的话](https://instagram-engineering.com/bringing-wide-color-to-instagram-5a5481802d7d)，或是错失节省开销的机会。  在 iOS 12 之后，`UIGraphicsImageRenderer` 会自动帮你选择正确的方案。

最后别忘记了，很多图片并不是拍摄出来的，而是通过绘图绘制的。 这里并不是刻意重复我写过的东西，只是怕你之前错过了: 

```swift
let circleSize = CGSize(width: 60，height: 60)

UIGraphicsBeginImageContextWithOptions(circleSize，true，0)

// Draw a circle
let ctx = UIGraphicsGetCurrentContext()!
UIColor.red.setFill()
ctx.setFillColor(UIColor.red.cgColor)
ctx.addEllipse(in: CGRect(x: 0，y: 0，width: circleSize.width，height: circleSize.height))
ctx.drawPath(using: .fill)

let circleImage = UIGraphicsGetImageFromCurrentImageContext()
UIGraphicsEndImageContext()
```

这个圆形图片使用的是每个像素 4 字节格式。 如果你使用 `UIGraphicsImageRenderer` 那么渲染器会自动选择合适的格式，为每个像素节省 75% 的内存消耗。

```swift
let circleSize = CGSize(width: 60，height: 60)
let renderer = UIGraphicsImageRenderer(bounds: CGRect(x: 0，y: 0，width: circleSize.width，height: circleSize.height))

let circleImage = renderer.image{ ctx in
    UIColor.red.setFill()
    ctx.cgContext.setFillColor(UIColor.red.cgColor)
    ctx.cgContext.addEllipse(in: CGRect(x: 0，y: 0，width: circleSize.width，height: circleSize.height))
    ctx.cgContext.drawPath(using: .fill)
}
```

## 缩小分辨率 vs 缩小采样
让我们跳过简单绘图的场景 - 还有非常多与图像相关的内存问题，源自真实的摄影图片。 比如人像，风景照。

对于一些工程师来说，他们有理由（逻辑上也说得过去）相信，通过 `UIImage` 简单地缩小图像尺寸就足够了。 但由于上面提及的原因，这通常来说不够，而且据 Apple 员工 Kyle Howarth 描述这也没有那么高效。

如我们之前讨论渲染路径时提到的，`UIImage` 会产生内存问题的主要原因是它会将原始图像加载到内存中进行解压。 理想状态下，我们应该减少图像缓存区的大小。

幸运的是，我们其实可以只以调整图像文件的大小为代价，来影响图像内存大小。 通常人们会假设这就是系统如何实现的，但其实不是。

让我们用点底层 API 来缩小采样试试:

```swift
let imageSource = CGImageSourceCreateWithURL(url，nil)!
let options: [NSString:Any] = [kCGImageSourceThumbnailMaxPixelSize:400，
                               kCGImageSourceCreateThumbnailFromImageAlways:true]

if let scaledImage = CGImageSourceCreateThumbnailAtIndex(imageSource，0，options as CFDictionary) {
    let imageView = UIImageView(image: UIImage(cgImage: scaledImage))
    
    imageView.translatesAutoresizingMaskIntoConstraints = false
    imageView.contentMode = .scaleAspectFit
    imageView.widthAnchor.constraint(equalToConstant: 300).isActive = true
    imageView.heightAnchor.constraint(equalToConstant: 400).isActive = true
    
    view.addSubview(imageView)
    imageView.centerXAnchor.constraint(equalTo: view.centerXAnchor).isActive = true
    imageView.centerYAnchor.constraint(equalTo: view.centerYAnchor).isActive = true
}
```

再次运行，我们得到的显示效果和之前一样。 但在这里，我们使用了 `CGImageSourceCreateThumbnailAtIndex()` 而不是直接将原始图像放在 image view  中。 真相大白的时刻到了，让我们通过 `vmmap` 来看看我们的优化是否奏效（再一次，为了简洁只截取了部分）: 

```
vmmap -summary baylorOptimized.memgraph

Physical footprint:         56.3M
Physical footprint (peak):  56.7M
```

节省的开销都统计在了一起。 如果我们将之前的 69.5M 和现在的 56.3M 进行对比，我们节约了 13.2M。 这是个很大的节省，几乎是整个图片的大小。

再进一步，你可以根据你的需要通过各种选项来打磨。 在 WWDC 2018 Session 219 "Images and Graphics Best Practices" 中，Apple 工程师 Kyle Sluder 通过使用 `kCGImageSourceShouldCacheImmediately` 标记来展示了一个很有趣的技巧控制解码: 

```swift
func downsampleImage(at URL:NSURL，maxSize:Float) -> UIImage
{
    let sourceOptions = [kCGImageSourceShouldCache:false] as CFDictionary
    let source = CGImageSourceCreateWithURL(URL as CFURL，sourceOptions)!
    let downsampleOptions = [kCGImageSourceCreateThumbnailFromImageAlways:true，
                             kCGImageSourceThumbnailMaxPixelSize:maxSize
                             kCGImageSourceShouldCacheImmediately:true，
                             kCGImageSourceCreateThumbnailWithTransform:true，
                             ] as CFDictionary
    
    let downsampledImage = CGImageSourceCreateThumbnailAtIndex(source,  0, downsampleOptions)!
    
    return UIImage(cgImage: downsampledImage)
}
```

Core Graphics 并不会参与解码图片，直到你明确需要使用缩略图的时候。 并且需要注意传入 `kCGImageSourceCreateThumbnailMaxPixelSize`，就像我们做的上面两个例子那样。 如果你不传，那么你会得到一个和原始图像一样大小的缩略图。 据文档描述: 

> “…如果没有指定最大像素大小，那么缩略图就会是完整的图片大小，这可能不是你想要的。”
>  “…if a maximum pixel size isn’t specified,  then the thumbnail will be the size of the full image, which probably isn’t what you want.”

那么这里发生了什么?  简单来说，我们通过在缩略图上使用了缩小部分图片的等式，创建了一个小得多的解码图像缓冲区。 回忆一下之前提到的渲染路径，第一步（加载）现在我们没有创建一个原始图像大小的缓冲区，而是一个 image view 显示大小的缓冲区。

想要一个这篇文章的太长不读版本? 找机会降低图像采样，而不是使用 `UIImage` 缩小图片。

## 附加部分
我个人在 Tandem 中配合着 [prefetch API](https://developer.apple.com/documentation/uikit/uitableviewdatasourceprefetching?language=swift) （iOS 11） 使用了这种技术。 但要记住即使我们在真正使用 table view 或者 collection view 之前这样做，我们在解码图片的时候，内部依然会带来的一个 CPU 使用量的高峰。 

尽管 iOS 在面对持续性能消耗时有很高效的处理方案，但在我们的例子中，可能是时不时才会产生这样的高峰。 所以在处理这种问题的时候，最好把希望寄予你自己创建的队列。 另一个优势是，这样还能将解码移动到后台处理。

快遮住眼睛，我业余项目中的 Objective-C 代码要出来了: 

```objc
//  用你自己的队列而不是 global 队列可以避免潜在的线程爆炸

- (void)tableView:(UITableView *)tableView prefetchRowsAtIndexPaths:(NSArray<NSIndexPath *> *)indexPaths
{
    if (self.downsampledImage != nil || 
        self.listItem.mediaAssetData == nil) return;
    
    NSIndexPath *mediaIndexPath = [NSIndexPath indexPathForRow:0
                                                     inSection:SECTION_MEDIA];
    if ([indexPaths containsObject:mediaIndexPath])
    {
        CGFloat scale = tableView.traitCollection.displayScale;
        CGFloat maxPixelSize = (tableView.width - SSSpacingJumboMargin) * scale;
        
        dispatch_async(self.downsampleQueue，^{
            // 缩减采样
            self.downsampledImage = [UIImage downsampledImageFromData:self.listItem.mediaAssetData
                               scale:scale
                        maxPixelSize:maxPixelSize];
            
            dispatch_async(dispatch_get_main_queue()，^ {
                self.listItem.downsampledMediaImage = self.downsampledImage;
            });
        });
    }
}
```

> 注意在你有大量的原始图像（raw image）资源时使用资源管理（asset catalogs）。
> 因为它会帮你管理缓存大小（还有其他很多的优势）

想要了解更多关于图像和内存管理的信息，可以关注这些信息量巨大的 WWDC 18 session:   
- [iOS Memory Deep Dive](https://developer.apple.com/videos/play/wwdc2018/416/?time=1074)
- [Images and Graphics Best Practices](https://developer.apple.com/videos/play/wwdc2018/219/)

## 总结一下
你无法察觉你不知道的东西。 就编程来说，你基本上相当于报名参加了一个需要持续跑每小时 10，000 米以跟上创新和变革的职业生涯。  这意味着...有大量的 API，框架，设计模式或者优化方案你并不知晓。 

在图像领域尤其是这样。 大多数时间，你可能只是初始化了一个 `UIImageView` 然后放进了一些好看的像素，就过了。 我知道啦，摩尔定理什么的。 现在这些电话运行速度很快，而且有数 G 的内存，并且我们把人类运送到了月球上，都只用了一台不到 100K 内存的电脑。

但是和魔鬼共舞不会长久，他必然需要滋养他的角。 别让系统杀掉你的应用，只是因为你用了 1G 内存来展示一张自拍照。 但愿这些知识和技巧可以将你拯救于崩溃日志。

下次见 ✌️。