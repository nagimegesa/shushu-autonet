# 上海大学校园网自动连接脚本

上海大学自动连接校园网络的Python脚本，支持有线/无线网络检测和浏览器自动化认证。
改项目灵感直接来源于[项目shu-auto-net
](https://github.com/DongZhouGu/shu-auto-net)。但是该项目已经很多年没有更新，所以重写了一个版本。

## 环境要求

### Python版本
- Python 3.10 或更高版本

### 依赖包
安装所需依赖：
```bash
pip install -r requirements.txt
```

### 浏览器驱动
- Microsoft Edge浏览器（最新版）
- 对应的Edge WebDriver
  - 下载地址：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
  - 下载后解压到 `edgedriver_win64` 目录
  - 或将WebDriver添加到系统PATH中

## 配置说明

### 1. 编辑配置文件
在脚本开头修改默认配置：
```python
DEFAULT_USER_NAME = "xxx"  # 你的学号
DEFAULT_PASSWD = "xxx"     # 你的密码
```

### 2. Wi-Fi设置
默认连接 `Shu(ForAll)` Wi-Fi网络，如需修改可在命令行参数中指定。

## 使用方法

### 基本使用
```bash
python main.py
```

### 命令行参数
```bash
python campus_network.py [选项]

选项:
  -h, --help            显示帮助信息
  -u, --username TEXT   校园网账号（学号）
  -p, --password TEXT   校园网密码
  -s, --ssid TEXT       Wi-Fi网络名称（默认：Shu(ForAll)）
  --headless            无头模式（不显示浏览器界面）
```

### 使用示例

1. **使用默认配置**（需要提前在脚本中设置用户名密码）
   ```bash
   python campus_network.py
   ```

2. **通过命令行指定账号密码**
   ```bash
   python campus_network.py -u 学号 -p 密码
   ```

3. **指定不同Wi-Fi网络**
   ```bash
   python campus_network.py -u 学号 -p 密码 -s "Wi-Fi名称"
   ```

4. **后台无头模式运行**
   ```bash
   python campus_network.py -u 学号 -p 密码 --headless
   ```

## 工作原理

1. **网络状态检测**
   - 检查是否已连接互联网
   - 检查是否连接到校园网（未认证状态）
   - 识别当前网络类型（有线/无线）

2. **网络连接**
   - 如果未连接网络，自动连接指定Wi-Fi
   - 等待网络获取IP地址

3. **认证登录**
   - 自动打开浏览器访问认证页面
   - 填写用户名和密码
   - 提交登录表单
   - 验证登录结果

## 日志说明

脚本运行时会产生详细日志，包括：
- 网络状态检测结果
- 网络连接过程
- 认证登录状态
- 错误和异常信息

日志格式示例：
```
2024-01-01 10:00:00 - __main__ - INFO - 当前网络状态: 仅连接校园网（未认证）
2024-01-01 10:00:00 - __main__ - INFO - 网络类型: 无线网络, 接口: Wi-Fi
```

## 常见问题

### 1. WebDriver相关问题
**问题**: `selenium.common.exceptions.WebDriverException: Message: 'msedgedriver' executable needs to be in PATH.`

**解决方案**:
1. 确保已下载对应版本的Edge WebDriver
2. 将 `msedgedriver.exe` 放在 `edgedriver_win64` 目录下
3. 或将其添加到系统PATH环境变量中

### 2. 依赖安装问题
**问题**: `ModuleNotFoundError: No module named 'pywifi'`

**解决方案**:
```bash
# 重新安装依赖
pip install -r requirements.txt
```

### 3. Wi-Fi连接失败
**可能原因**:
- Wi-Fi网络名称不正确
- 系统权限不足
- 网络适配器问题

**解决方案**:
- 检查Wi-Fi名称是否正确：`python main.py -s "正确的Wi-Fi名称"`

### 4. 认证页面变化
**问题**: 校园网认证页面更新导致脚本失效

**解决方案**:
更新脚本中的页面元素选择器：
```python
# 修改认证页面相关的元素选择器
self.driver.execute_script(f"document.getElementById(arguments[0]).value = arguments[1];", "username", self.username)
self.driver.execute_script(f"document.getElementById(arguments[0]).value = arguments[1];", "pwd", self.password)
```

**设置自启动和定时任务**
1. windows

    参考链接：https://blog.csdn.net/u012849872/article/details/82719372

2. Linux 

    都用Linux了，你肯定懂的。

3. 使用其他浏览器

    脚本默认使用Microsoft Edge浏览器。如果需要使用其他浏览器，需要修改脚本中的浏览器驱动配置。
    例如，使用Chrome浏览器需要下载Chrome WebDriver并替换 `msedgedriver.exe`。并修改脚本中的浏览器驱动配置。

## 注意事项

1. **安全性**: 不建议在脚本中硬编码密码，建议通过命令行参数或环境变量传入
2. **权限**: 在某些系统上可能需要管理员权限操作网络适配器
3. **兼容性**: 脚本主要针对Windows系统设计，其他系统可能需要调整
4. **合法性**: 仅限个人使用，请遵守校园网使用规定

## 许可证
本项目仅供学习和个人使用，请勿用于商业用途。

---
**重要提示**: 使用前请确保你有权使用该网络服务，并遵守相关法律法规和学校规定。