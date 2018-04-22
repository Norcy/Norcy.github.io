---
title: Objective-C中的消息转发机制
date: 2016-09-25
categories:
- iOS
photos: 
keywords: Objective-C;objc_msgSend;消息转发;runtime;dynamic;
---

# Objective-C 中函数调用的实质

```objc
id returnValue = [someObj messageName:params];

// 运行时转化为
id returnValue = objc_msgSend(someObj, @selector(messageName:), params);
```
注意：

从该接收者所属的类的方法列表中寻找（每次找到都会缓存下，以供下次查找用），找不到就沿着继承树向上搜索，最后还是没找到，就执行消息转发

# 消息转发分为三大阶段
第一阶段先征询消息接收者所属的类，看其是否能动态添加方法，以处理当前这个无法响应的 selector，这叫做__动态方法解析__（dynamic method resolution）。如果运行期系统（runtime system） 第一阶段执行结束，接收者就无法再以动态新增方法的手段来响应消息，进入第二阶段。

第二阶段看看有没有其他对象（备援接收者，replacement receiver）能处理此消息。如果有，运行期系统会把消息转发给那个对象，转发过程结束；如果没有，则启动完整的消息转发机制。

第三阶段 完整的消息转发机制。运行期系统会把与消息有关的全部细节都封装到 NSInvocation 对象中，再给接收者最后一次机会，令其设法解决当前还未处理的消息。

![](http://7xsd8c.com1.z0.glb.clouddn.com/msgSend.png)

## 动态方法解析
对象在收到无法响应的消息后，会调用其所属类的下列方法

```objc
/**
 *  如果尚未实现的方法是实例方法，则调用此函数
 *
 *  @param selector 未处理的方法
 *
 *  @return 返回布尔值，表示是否能新增实例方法用以处理selector
 */
+ (BOOL)resolveInstanceMethod:(SEL)selector;
/**
 *  如果尚未实现的方法是类方法，则调用此函数
 *
 *  @param selector 未处理的方法
 *
 *  @return 返回布尔值，表示是否能新增类方法用以处理selector
 */
+ (BOOL)resolveClassMethod:(SEL)selector;
```

## 备援接收者
如果无法动态解析方法，运行期系统就会询问是否能将消息转给其他接收者来处理，对应的方法为

```objc
/**
 *  此方法询问是否能将消息转给其他接收者来处理
 *
 *  @param aSelector 未处理的方法
 *
 *  @return 如果当前接收者能找到备援对象，就将其返回；否则返回nil；
 */
- (id)forwardingTargetForSelector:(SEL)aSelector;
```

## 完整的消息转发机制
如果前面两步都无法处理消息，就会启动完整的消息转发机制。首先创建 NSInvocation 对象，把尚未处理的那条消息有关的全部细节装在里面，在触发 NSInvocation 对象时，消息派发系统（message-dispatch system）将会把消息指派给目标对象。对应的方法为

```objc
/**
 *  消息派发系统通过此方法，将消息派发给目标对象
 *
 *  @param anInvocation 之前创建的NSInvocation实例对象，用于装载有关消息的所有内容
 */
- (void)forwardInvocation:(NSInvocation *)anInvocation;
```

# 例子：利用消息转发机制实现@dynamic属性
.h

```objc
#import <Foundation/Foundation.h>

@interface NCYAutoDictionary : NSObject
@property (nonatomic,strong) NSString *myName;
@end
```
.m

```objc
#import "NCYAutoDictionary.h"
#import <objc/message.h>

id autoDictionaryGetter(id self, SEL _cmd);
void autoDictionarySetter(id self, SEL _cmd, id value);

@interface NCYAutoDictionary ()
@property (nonatomic, strong) NSMutableDictionary *backingStore;
@end

@implementation NCYAutoDictionary
@dynamic myName;

- (instancetype)init
{
	if (self = [super init])
	{
		_backingStore = [NSMutableDictionary new];
	}
	return self;
}

id autoDictionaryGetter(id self, SEL _cmd)
{
	NCYAutoDictionary *typeSelf = (NCYAutoDictionary *)self;
	NSMutableDictionary *backingStore = typeSelf.backingStore;

	NSString *key = NSStringFromSelector(_cmd);

	return [backingStore objectForKey:key];
}

void autoDictionarySetter(id self, SEL _cmd, id value)
{
	NCYAutoDictionary *typeSelf = (NCYAutoDictionary *)self;
	NSMutableDictionary *backingStore = typeSelf.backingStore;

	NSString *seletorString = NSStringFromSelector(_cmd);

	NSMutableString *key = [seletorString mutableCopy];

	// 将 "setSomething:" 转为 "something"
	// remove :
	[key deleteCharactersInRange:NSMakeRange(key.length - 1, 1)];

	// remove set
	[key deleteCharactersInRange:NSMakeRange(0, 3)];

	// lowercase the first character
	NSString *lowercaseFirstChar = [[key substringToIndex:1] lowercaseString];

	[key replaceCharactersInRange:NSMakeRange(0, 1) withString:lowercaseFirstChar];

	if (value)
	{
		[backingStore setObject:value forKey:key];
	}
	else
	{
		[backingStore removeObjectForKey:key];
	}
}

// 运行时动态添加方法，对于同一个SEL，执行完该函数后，就不会再次走到这里，因为方法已经添加到类中去了（程序运行时都有效）
+ (BOOL)resolveInstanceMethod:(SEL)sel
{
	NSString *selectorString = NSStringFromSelector(sel);
	if ([selectorString hasPrefix:@"set"])
	{
		class_addMethod(self, sel, (IMP)autoDictionarySetter, "v@:@");
	}
	else
	{
		class_addMethod(self, sel, (IMP)autoDictionaryGetter, "@@:");
	}
	return true;
}
@end
```

测试

```objc
NCYAutoDictionary *myDic = [[NCYAutoDictionary alloc] init];
myDic.myName = @"Norcy";
NSLog(@"%@", myDic.myName);   // 打印"Norcy"
```
## 注意
1. 对于同一个SEL，执行完 `resolveInstanceMethod:` 后，下次调用该SEL的方法时，就不会再次执行 `resolveInstanceMethod:`，因为方法已经添加到类中去了（程序运行时都有效）
2. `class_addMethod(self, sel, (IMP)autoDictionarySetter, "v@:@");`

    最后一个参数是编码格式，详见[苹果官方文档](https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html)
3. `autoDictionarySetter`的参数是怎么确定的？

    因为外部调用的时候其实是 `[myDic setMyName:@"Norcy"]`
    
    即 `objc_msgSend(myDic, @selector(setMyName:), @"Norcy")`
    
    经过 `resolveInstanceMethod:` 替换之后，`setMyName:` 的消息都会转发给 `autoDictionarySetter` 来实现
    
    `autoDictionarySetter` 是一个 IMP，默认的参数就有2个，id self 和 SEL _cmd，最后一个参数 value 是 `setMyName:` 带过来的参数，以此确定

# 参考文章
+ 《Effective Objective-C 2.0》第11条和第12条
