---
title: iOS的单例模式与多线程安全
date: 2017-04-05
categories:
- iOS
photos: 
keywords: iOS;单例模式;多线程安全;dispatch_once;
---

# 版本1

```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    if (sharedInstance == nil)
    {
        sharedInstance = [[self alloc] init];
    }
    return sharedInstance;
}
```

版本1采用 static 变量方法，先判断实例是否已初始化，如果已初始化则直接返回，否则创建实例

缺点是多线程下不安全。如果多个线程同时访问 sharedInstance，可能会有多个线程同时通过`(sharedInstance == nil)`的条件检查，于是，多个实例就创建出来

# 版本2

```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    if (sharedInstance == nil)
    {
        @synchronized (self) 
        {
            sharedInstance = [[self alloc] init];
        }
    }
    return sharedInstance;
}
```

为了线程互斥，那么版本2在版本1的基础上添加 @synchronized

多线程的安全问题得到解决了吗？没有。依然可能有多个线程同时通过非空检查，现在它们变成按顺序地创建了多个实例

# 版本3

```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    @synchronized (self)
    {
        if (sharedInstance == nil)
        {
            sharedInstance = [[self alloc] init];
        }
    }
    return sharedInstance;
}
```

在版本2的基础上，只要把非空检查也放到 @synchronized 里面，那么就不会出现多个线程同时通过非空检查了，所以多线程的安全问题就得到解决了。

但是现在每次访问 sharedInstance，无论单例是否已经初始化完毕，都要对 self 加锁，是非常浪费的

# 版本4

```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    if (sharedInstance == nil)
    {
        @synchronized (self)
        {
            if (sharedInstance == nil)
            {
                sharedInstance = [[self alloc] init];
            }
        }
    }
    return sharedInstance;
}
```

版本4是版本3的升级版本，称为“Double Check”。

1. 如果单例已创建，则直接返回，不需要加锁；
2. 如果单例没创建，则加锁
3. 加锁后，只能有一个线程通过非空检查，创建单例

很完美，但是写起来有点复杂

# 终极版本

```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedInstance = [[self alloc] init];
    });
    return sharedInstance;
}
```

使用 dispatch_once，秒杀以上方案，更快更安全

Tips：把上述代码保存到代码片段，直接丢到任何类里面都适用

# 由单例模式引发的多线程安全的思考
## static bool 的判断在多线程下不安全

```objc
static bool hasDone = NO;
if (!hasDone)
{
    // do something
    hasDone = YES;
}
// do something
```

以上写法不安全，有可能多个线程同时通过非空检查，导致 if 体内的代码执行多次

如果一段代码是在 App 声明周期内只执行一次，则推荐使用 `dispatch_once`；其他的情况要具体分析

## 懒加载在多线程下不安全

```objc
- (NSArray *)myArray
{
    if (_myArray)
    {
        _myArray = [[NSArray alloc] init];
    }
    return _myArray;
}
```

这种判断在多线程下不安全的。所以多线程下尽量别使用懒加载，即使使用，也要加相应的保护，比如在 `_myArray` 不会被重新置为 nil 的前提下可以使用 `dispatch_once`