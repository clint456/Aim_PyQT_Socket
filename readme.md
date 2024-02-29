## 需求：
接收：
1. 接收视频帧 【已完成】
2. 接收yolo识别出来的坐标 

发送：
1. 射击指令
2. 追踪目标(目标位置)
   `格式: x,y,flag`

## bug
1. 播放按键逻辑 【已解决】
2. ui界面布局
3. 

## 加急：
1. 发送socket数据包给下机位 

## 日志
---
#### 2-29-9:39报错日志
```bash
e:\workspace\PyQt\dev_project\Aim\GUI\main.py:327: DeprecationWarning: 'exec_' will be removed in the future. Use 'exec' instead.
  sys.exit(app.exec_()) 

  ----> 修改 : 更改pyside6库后要使用下面的方法调用
  sys.exit(app.exec_()) 
  --> sys.exit(app.exec())


e:\workspace\PyQt\dev_project\Aim\GUI\main.py:88: DeprecationWarning: Function: 'QMouseEvent.globalPos() const' is marked as deprecated, please check the documentation for more information.
  global_pos = event.globalPos()
  ----> 说明：此方法在本版本可以正常运行，但是即将启用，后期如果更新版本，需要更改


反序列化时出错：invalid load key, '\x00'.
接收视频时发生错误：local variable 'frame' referenced before assignment
反序列化时出错：invalid load key, '\x00'.
接收视频时发生错误：local variable 'frame' referenced before assignment
反序列化时出错：invalid load key, '\x1a'.
接收视频时发生错误：local variable 'frame' referenced before assignment

  ----> 说明： socket加载视频帧的方法存在问题，但是目前不影响运行
```
---