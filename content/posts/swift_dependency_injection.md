---
title: "iOS 架构之另一种依赖注入的思路"
date: "2022-03-15"
tags: ["Swift"]
description: "介绍了一种相比 protocol 更轻量级更灵活的依赖注入实现"
---

在 iOS 业务开发过程经常面对网络请求，数据持久化这样带有副作用的操作。为了能够在测试中 mock 这些操作，通常的做法就是抽象一层 protocol 出来，然后编写不同的实现。

比如需要处理一个简陋的注册业务（示例省略了一点细节），需要用户输入信息后发送网络请求，成功后返回对应用户对象。

首先为网络请求定义一个 protocol：

```swift
protocol SignUpRepositoryProtocol: RepositoryProtocol {
    func handleSignUp(name: String, email: String, pwd: String) -> AnyPublisher<User, Error> 
}
```

对其进行实现：

```swift
struct SignUpRepository: SignUpRepositoryProtocol {
    func handleSignUp(name: String, email: String, pwd: String) -> AnyPublisher<User, Error> {
        client(.signUp(name, email, pwd))
            .map
            .decode
            .eraseToAnyPublisher()
    }
}
```

将其注入到  `ViewModel` 或是 `Interactor` 中（取决于你采取的架构是什么 :p ），并且调用对应方法：

```swift
class SignUpViewModel {
    enum State {
      case loading
      case success
      case failed
    }
    let repository: SignUpRepositoryPortocol
    var state: State = .loading
    init(repository: SignUpRepositoryPortocol) {
        self.repository = repository
    }

    func onSubmit(name: String, email: String, pwd: String) {
        repository.hanldeSignUp(name: name, email: email, pwd: pwd)
          .sink {[weak self] completion in 
            switch completion {
              case .failure: 
                self.?state = .failed
              case .finished: break
            }
          } receiveValue: {[weak self] result in 
              self?.state = .success
          }.store(in: &bag)
    }
}
```

由此如果需要测试对应的方法，只需要再创建一份  `MockSignUpRepository` 的实现即可，比如想要测试注册成功或失败场景下的处理：

```swift
struct MockSignUpRepository: SignUpRepositoryPortocol {
    let shouldSignUpSuccess: Bool
    
    func handleSignUp(name: String, email: String, pwd: String) -> AnyPublisher<User, Error> {
        if shouldSignUpSuccess {
            Just(User.mock)
                .mapError{ _ in SignUpError.someError }
                .eraseToAnyPublisher()
        } else {
            Fail(error: SignUpError.someError)
                .eraseToAnyPublisher() 
        }
    }
}
```

在编写测试的时候，传入 `SignUpViewModel` 的依赖替换成我们想要测试的 Mock 实现：

```swift
func shouldSignUpSuccessWhenXXX() {
    // Given
    let sut = SignUpViewModel(repository: MockSignUpSuccessRepository(shouldSignUpSuccess: true))
  
    // When
    sut.onSubmit(...) // 合法输入
  
    // Then
    XCTAssertEqual(sut.state, .success)
}

func shouldSignUpFailWhenXXX() {
    // Given
    let sut = SignUpViewModel(repository: MockSignUpSuccessRepository(shouldSignUpSuccess: false))
  
    // When
    sut.onSubmit(...) // 非法输入
  
    // Then
    XCTAssertEqual(sut.state, .failed)
}
```

这时候似乎一切都很美好，但现在再补充一些业务需求，如果需要返回不同的错误类型怎么办？比如用户名错误，那就需要额外的布尔值来表示；再比如邮箱错误，那又需要增加新的布尔值。而这还仅仅只是一个方法的几个分支逻辑处理。当出现较多的逻辑分支之后，如果我们实际的业务再发生变动需要重构，那还得去对 Mock 类也进行重构，同时还需要确保这些控制逻辑分支的布尔值也得到了正确的更新。

```swift
let sut = SignUpViewModel(
    repository: MockSignUpSuccessRepository(
        shouldSignUpSuccess: false, 
        shouldShowUsernameError: true,
        shouldShowEmailError: true,
        shouldUsernamePassValidation: true,
        shouldEmailPassValidation: true,
        // ...😱
   )
)
```

这时候就可以介绍另一种依赖注入方式了。首先定义一个 `Repository` 对象，这个对象就像之前的 `Repository` 一样，区别是网络请求通过一个属性来持有，同时会提供一个标记为 private 的默认实现：

```swift
struct Repository {  
    var handleSignUp = handleSignUp(name:, email:, pwd:)
}

private func handleSignUp(name: String, email: String, pwd: String) -> AnyPublisher<User, Error> {
    client(.signUp(name, email, pwd))
        .map
        .decode
        .eraseToAnyPublisher()
}
```

然后将这个 `Repository` 实例放到一个 `Environment` 对象中：

```swift
struct Environment {
    var repo = Repository()
}
```

同时替换 ViewModel 中之前对 `Repository` 的引用：
```swift
class SignUpViewModel {
    enum State {
      case loading
      case success
      case failed
    }
    // let repository: SignUpRepositoryPortocol
    let current: Environment // 👈
    var state: State = .loading
    
    init(current: Environment) {
        self.current = current // 👈
    }

    func onSubmit(name: String, email: String, pwd: String) {
        current.repo.hanldeSignUp(name, email, pwd) // 👈
          .sink { completion in 
            switch completion {
              case .failure: 
                self.state = .failed
              case .finished: break
            }
          } receiveValue: {[weak self] result in 
              self?.state = .success
          }.store(in: &bag)
    }
}
```

代码几乎和之前相同，但保持了更高的可替换性，怎么体现的呢？需要 mock 网络请求 时，可以给 Repository 创建一个 extension：

```swift
extension Repository {
    static let mock = Repository(
        handleSignUp: Just(User.mock)
                          .mapError{ _ in SignUpError.someError }
                          .eraseToAnyPublisher()
    )
}
```

然后在测试代码构建 ViewModel 的时候就可以将 Mock 传递进去：

```swift
func shouldSignUpSuccessWhenXXX() {
    // Given
    let sut = SignUpViewModel(current: Environment(repo: Repository.mock))
  
    // When
    sut.onSubmit(...) // 合法输入
  
    // Then
    XCTAssertEqual(sut.state, .success)
}
```

对于方法多分支的逻辑，则可以独立实现一份，而不是重新创建整个  `MockRepository`  类或者是用一些变量来控制分支逻辑：

```swift
func shouldSignUpSuccessWhenXXX() {
    // Given
    let sut = SignUpViewModel(
        current: Environment(
            repo: Repository(handleSignUp: 
                Fail(error: SignUpError.someError).eraseToAnyPublisher()
            )
        )
    )
  
    // When
    sut.onSubmit(...) // 非法输入
  
    // Then
    XCTAssertEqual(sut.state, .success)
}
```

这种方式来注入依赖的优势在于：

- 不需要像 protocol 那样写太多模版代码
- mock 的逻辑分支很容易可以实现相互独立的版本
- 依赖的副作用会更容易 mock，特别是系统类