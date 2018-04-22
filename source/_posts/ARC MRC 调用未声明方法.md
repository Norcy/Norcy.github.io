---
title: ARC/MRC 调用未声明方法
date: 2016-06-15
categories:
- iOS
keywords: ARC,MRC,未声明方法,performSelector,undeclared methods
---

# 背景
有一次，发现调用一个未声明的方法的时候，Xcode 居然没有像往常一样给出错误提示，而只是给了 Warning，研究后发现原来该文件不是 ARC，所以出现这种问题，那么 ARC 和 MRC 之间，对于调用未声明的方法，有什么区别呢？
# 实验
`[self noSuchMethod];`

MRC 下，调用一个未声明的方法，编译器会给出 Warning:
> "Instance method 'noSuchMethod' not found (return type defaults to 'id')"

ARC 下，调用一个未声明的方法，编译器却给出 Error:
> "No visible @interface for 'xxx' declares the selector 'noSuchMethod'"


原因：

ARC 下，编译器需要知道方法返回值的所有者，才能正确在合适的地方添加 retain/release 等，所以显式调用一个未声明的方法在 ARC 下默认是不允许的

下面是具体的代码提示，跟Xcode的版本有关系，我的Xcode是`Version 7.3.1 (7D1014)`

MRC:

```objectivec
id classA;

// Warning:Instance method '-xyz' not found (return type defaults to 'id')
[classA xyz];

// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz)];

// No Error, No Warning
[classA performSelector:NSSelectorFromString(@"xyz")];

// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz) withObject:nil];
    
// No Error, No Warning
[classA performSelector:NSSelectorFromString(@"xyz") withObject:nil];
    
// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz) withObject:nil afterDelay:0];

// No Error, No Warning
[classA performSelector:NSSelectorFromString(@"xyz") withObject:nil afterDelay:0];
```

ARC:

```objectivec
id classA;
    
// Error:No known instance method for selector 'xyz' 或者
// Error:No visible @interface for 'xxx' declares the selector 'xyz'
[classA xyz];
    
// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz)];
    
// Warning:"PerformSelector may cause a leak because its selector is unknown"
[classA performSelector:NSSelectorFromString(@"xyz")];
    
// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz) withObject:nil];
    
// Warning:"PerformSelector may cause a leak because its selector is unknown"
[classA performSelector:NSSelectorFromString(@"xyz") withObject:nil];
    
// Warning:Undeclared selector 'xyz'
[classA performSelector:@selector(xyz) withObject:nil afterDelay:0];
    
// No Error, No Warning
[classA performSelector:NSSelectorFromString(@"xyz") withObject:nil afterDelay:0];
```

问题：

1. @selector 和 NSSelectorFromString 区别

    可以看到使用 @selector()，编译器可以知道相应方法没有被声明；而使用 NSSelectorFromString，编译器并不知情，因为该方法是动态的，在 Runtime 的时候才能确定相应的方法实现，所以编译器选择了忽略
    
    所以 MRC 下很简单，@selector 就给警告， NSSelectorFromString 就不管
    
    ARC 下，就复杂点，@selectot 依然给警告，但是 NSSelectorFromString 的处理就复杂点，继续往下看
    
2. 那为什么 ARC 下， `performSelector:NSSelectorFromString()` 会有 Leak Warning
    
    事实上，无论 xyz 方法存在不存在，只要是 ARC 下，使用`performSelector:NSSelectorFromString()`就会有该 Warning 产生，因为编译器并不知道你调用了什么方法(是含有`alloc`/`new`/`copy`/`mutableCopy`关键字的方法还是普通方法)，那它也不知道该不该添加 retain/release 等，所以给出可能产生内存泄露的警告
    
    如果确定了这样调用没有内存问题，那么可以通过以下方法消除 Warning：
    
    + 针对部分代码
    
    ```objectivec
    #pragma clang diagnostic push
    #pragma clang diagnostic ignored "-Warc-performSelector-leaks"
    [classA performSelector:NSSelectorFromString(@"xyz")];
    #pragma clang diagnostic pop
    ```

    更骚一点的做法是
    
    ```objectivec
    #define SILENCE_PERFORMSELECTOR(expr)                               \
    do {                                                                \
    _Pragma("clang diagnostic push")                                    \
    _Pragma("clang diagnostic ignored \"-Warc-performSelector-leaks\"") \
    expr;                                                               \
    _Pragma("clang diagnostic pop")                                     \
    } while(0)
    
    SILENCE_PERFORMSELECTOR([classA performSelector:NSSelectorFromString(@"xyz")]);
    ```

    + 针对单个文件，与设置某个文件为非 ARC 类似（见小Tips），添加`-Wno-arc-performSelector-leaks`
    + 针对整个工程，Build Settings，搜索 Other Warning Flags，添加`-Wno-arc-performSelector-leaks`
    
3. 最后的问题，为什么 ARC 下， `performSelector:NSSelectorFromString() withObject:afterDelay:` 就没有 Leak Warning 呢
    
    看看这几个函数的原型
    
    ```objectivec
    - (id)performSelector:(SEL)aSelector;
    - (id)performSelector:(SEL)aSelector withObject:(id)object;
    - (void)performSelector:(SEL)aSelector withObject:(nullable id)anArgument afterDelay:(NSTimeInterval)delay;    
    ```
    可以看到，`performSelector:withObject:afterDelay:`返回值是 void。所以可以推测，Xcode 认为，你既然写了 afterDelay（即使是延迟0秒），那么它的返回值是 void，无论 selector 有没有返回值，都不需要为之添加 retain/release，所以这种情况下没有内存问题

# 小Tips
1. ARC 与 MRC 互转：工程 -> Targets -> Build Phases -> Compile Sources -> 对应的.m文件的Compiler Flags添加`-fno-objc-arc`(MRC)/`-fobjc-arc`(ARC)
2. 判断 ARC 与 MRC 的快速方法，在 `dealloc` 里面调用 `[super dealloc];`，如果报错则是 ARC，否则是 MRC

# 参考链接
+ [stackoverflow1](http://stackoverflow.com/questions/7017281/performselector-may-cause-a-leak-because-its-selector-is-unknown/7954697#7954697)
+ [stackoverflow2](http://stackoverflow.com/questions/20582642/why-arc-forbids-calls-to-undeclared-methods/20582863#20582863)