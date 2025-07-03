# Review Gate V2 for Cursor IDE - Windows 11 中文优化版

[![Review Gate V2](https://iili.io/3OtOp7R.th.png)](https://freeimage.host/i/3OtOp7R)

## 📖 项目简介

**Review Gate V2** 是基于 [LakshmanTurlapati/Review-Gate](https://github.com/LakshmanTurlapati/Review-Gate) 项目修改的 Windows 11 中文优化版本。

该工具可以让 **Cursor AI** 在完成任务后不立即结束对话，而是等待您的进一步指令，从而在单次请求中完成更深入的工作。这样可以将您的月度请求额度的价值最大化，让 500 次请求发挥出 2500 次的效果！

## ✨ 核心功能

* **🎯 智能等待机制**：AI 完成主要任务后会自动等待您的后续指令
* **💬 多模态交互**：支持文本输入、语音转文字、图片上传等多种交互方式
* **🔄 请求倍增器**：在单次请求生命周期内完成多轮深度工作
* **🖥️ Windows 11 优化**：专为 Windows 11 系统和中文环境优化
* **🎤 语音支持**：内置语音转文字功能，支持中文语音识别
* **📷 图像上传**：支持图片上传和分析功能

## 🎯 适用场景

* **复杂编程任务**：需要多轮优化和调试的代码开发
* **文档编写**：需要反复修改和完善的技术文档
* **架构设计**：需要多次讨论和调整的系统设计
* **代码审查**：深入的代码分析和优化建议

## 🛠️ 工作原理

1. **任务启动**：您向 Cursor 提交一个复杂任务（计为 1 次主请求）
2. **AI 执行**：Cursor AI 完成主要工作（使用部分工具调用额度）
3. **Review Gate 激活**：AI 自动打开交互弹窗等待您的进一步指令
4. **持续优化**：您可以通过文本、语音或图片提供后续指令
5. **深度完成**：AI 根据您的指令继续完善工作（使用剩余工具调用额度）
6. **循环迭代**：直到您输入 `TASK_COMPLETE` 或手动结束

## 🚀 一键安装

### 📋 系统要求

- **操作系统**：Windows 11
- **Python**：3.10 或更高版本
- **Cursor IDE**：最新版本
- **网络**：需要下载依赖包

### ⚠️ 重要提醒

**在安装前请备份您的 `mcp.json` 配置文件！**

安装脚本会覆盖 `%USERPROFILE%\.cursor\mcp.json` 文件。如果您已有其他 MCP 服务器配置，请先备份：

```powershell
copy "%USERPROFILE%\.cursor\mcp.json" "%USERPROFILE%\.cursor\mcp.json.backup"
```

### 🔧 安装步骤

1. **下载本项目**到本地
2. **运行安装脚本,双击打开即可**：
   ```batch
   install.bat
   ```

就这么简单！脚本会自动完成所有配置工作。

### 🌐 代理配置（可选）

如果您的网络环境需要代理，请在运行安装脚本前修改 `install.bat` 文件：

找到以下被注释的行：

```batch
@REM python -m pip install --upgrade pip --proxy=http://127.0.0.1:50470
@REM python -m pip install -r requirements_simple.txt --proxy=http://127.0.0.1:50470
```

取消注释并将 `50470` 改为您的代理端口：

```batch
python -m pip install --upgrade pip --proxy=http://127.0.0.1:您的端口
python -m pip install -r requirements_simple.txt --proxy=http://127.0.0.1:您的端口
```

## 📁 安装内容

安装完成后，以下组件将被安装到您的系统：

- **MCP 服务器**：`%USERPROFILE%\cursor-extensions\review-gate-v2\`
- **Python 虚拟环境**：包含所有必需的依赖包
- **Cursor 扩展**：Review Gate V2 扩展 (.vsix)
- **MCP 配置**：自动配置的 `mcp.json` 文件

## 🧪 测试安装

安装完成后，请按以下步骤测试：

1. **完全重启 Cursor IDE**
2. **测试手动触发**：按 `Ctrl+Shift+R`
3. **测试 AI 调用**：向 Cursor AI 说："请使用 review_gate_chat 工具"

## 🎤 语音功能使用

1. 在弹出的 Review Gate 窗口中点击**麦克风图标**
2. **清晰说话** 2-3 秒（支持中文）
3. 点击**停止按钮**完成录音
4. 系统会自动将语音转为文字

## 📷 图像上传功能

1. 在 Review Gate 窗口中点击**相机图标**
2. 选择要上传的图片（支持 PNG、JPG、GIF 等格式）
3. 图片将包含在您的响应中供 AI 分析

## 🔧 故障排除

### 常见问题

**Q: 安装后无法找到 Review Gate 工具？**
A: 请确保完全重启了 Cursor IDE，并检查扩展是否正确安装。

**Q: 语音功能不工作？**
A: 确保已安装 SoX，运行 `sox --version` 检查。

**Q: MCP 服务器无法启动？**
A: 检查 Python 环境是否正确安装，查看日志文件了解详细错误。

### 日志文件位置

```powershell
# 查看日志文件位置
python -c "import tempfile; print(tempfile.gettempdir())"
# 然后查看 review_gate_v2.log 文件
```

### 手动安装扩展

如果自动安装失败，请手动安装：

1. 打开 Cursor IDE
2. 按 `Ctrl+Shift+P`
3. 输入 "Extensions: Install from VSIX"
4. 选择：`%USERPROFILE%\cursor-extensions\review-gate-v2\review-gate-v2-2.7.3.vsix`

## 📝 更新日志

### Windows 11 中文优化版改进

- ✅ 修复了中文编码问题，在mcp中添加"PYTHONIOENCODING": "utf-8",review_gate_v2_mcp_fixed.py中添加了"utf-8"
- ✅ 优化了 Windows 11 兼容性
- ✅ 添加了中文语音识别支持
- ✅ 改进了安装脚本的用户友好性
- ✅ 增强了错误处理和日志记录

## 🙏 致谢

本项目基于 [Lakshman Turlapati](https://github.com/LakshmanTurlapati) 的 [Review-Gate](https://github.com/LakshmanTurlapati/Review-Gate) 项目开发。

感谢原作者的创新想法和开源贡献！

## 📄 许可证

本项目遵循原项目的许可证条款。

---

🎯 **让您的 Cursor AI 请求发挥最大价值，享受深度交互编程体验！** ✨
