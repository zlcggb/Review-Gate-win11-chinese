# Review Gate V2 for Cursor IDE - Windows 11 中文优化版

[![Review Gate V2](https://iili.io/3OtOp7R.th.png)](https://freeimage.host/i/3OtOp7R)

## 📖 项目简介

**Review Gate V2** 是基于 [LakshmanTurlapati/Review-Gate](https://github.com/LakshmanTurlapati/Review-Gate) 项目修改的 Windows 11 中文优化版本，旨在为 Cursor IDE 用户提供更稳定、更兼容 Windows 11 环境的 AI 交互体验。

## 🛠️ 工作原理

Review Gate V2 实现了 AI 与用户之间基于弹窗的多模态交互。其核心工作流程如下：

1.  **任务启动**：当 AI Agent 需要用户提供反馈、确认或有后续任务时，会通过 MCP (Model Context Protocol) 向 Cursor IDE 发送请求。
2.  **Review Gate 激活**：Cursor IDE 接收到请求后，会自动弹出一个交互式窗口（Review Gate 弹窗），等待用户输入。
3.  **用户交互**：用户可以在弹窗中输入文本、上传图片或通过语音进行反馈。
4.  **消息回传**：用户在弹窗中发送的内容会被 MCP 服务器接收并回传给 AI Agent。
5.  **循环迭代**：AI Agent 根据用户的反馈继续处理任务，并可再次激活 Review Gate 弹窗，实现持续的交互式对话，直到用户明确输入 `TASK_COMPLETE` 或任务完成。

## 🚀 一键安装

### 📋 系统要求

-   **操作系统**：Windows 11
-   **Python**：3.10 或更高版本 (推荐从 [Python 官方网站](https://www.python.org/downloads/windows/) 或 Microsoft Store 安装)
-   **Cursor IDE**：支持 MCP (Model Context Protocol) 功能的版本。
-   **网络连接**：需要下载 Python 依赖包和可能需要的 AI 模型文件。如果网络环境不佳，请参考下方的“代理配置”部分。

### ⚠️ 重要提醒

**在安装前，强烈建议手动备份您的 `mcp.json` 配置文件！**

安装脚本会覆盖 `%USERPROFILE%\.cursor\mcp.json` 文件。虽然脚本会自动创建带有时间戳的备份文件（例如 `mcp.json.backup.20231026_103000`），但为确保数据安全和您现有 MCP 配置的完整性，仍建议您在运行安装脚本前手动备份：

```powershell
copy "%USERPROFILE%\.cursor\mcp.json" "%USERPROFILE%\.cursor\mcp.json.backup.manual"
```

### 🔧 安装步骤

请按照以下步骤进行安装：

1.  **下载本项目到本地：**
    *   **通过 Git 克隆 (推荐)**：
        ```batch
        git clone https://github.com/zlcggb/Review-Gate-win11-chinese.git
        ```
    *   **或 直接下载项目压缩包**：从 GitHub 项目页面下载 `.zip` 压缩包并解压到您希望的目录。

2.  **运行安装脚本**：
    *   进入项目根目录。
    *   **双击运行 `install.bat` 文件**。
    *   脚本将自动检测 Python 环境、安装必要的依赖（包括 SoX，如果通过 Chocolatey 可用）、创建 Python 虚拟环境并配置 MCP 服务器。

3.  **安装 Cursor 扩展**：
    *   **拖拽安装 (推荐)**：打开 Cursor IDE 的扩展市场面板，然后将项目目录下的 `review-gate-v2-2.7.3.vsix` 文件直接拖拽到 Cursor 的扩展列表中，它将自动开始安装。
    *   **或 通过命令安装**：
        *   在 Cursor IDE 中按下 `Ctrl+Shift+P` (或 `F1`) 打开命令面板。
        *   输入并选择：`Extensions: Install from VSIX...`。
        *   在弹出的文件选择对话框中，导航到并选择：`%USERPROFILE%\.cursor\cursor-extensions\review-gate-v2\review-gate-v2-2.7.3.vsix`。
        *   点击“确认”进行安装。
4. **复制规则**：
       复制 `review-gate-v2.mdc` 到项目规则 `.cursor\rules\`, 总是启用
   
就这么简单！脚本会自动完成大部分配置工作。安装完成后，您可能需要**完全重启 Cursor IDE** 以确保所有更改生效。

### 🌐 代理配置（可选）

如果您的网络环境需要代理才能访问 PyPI (Python 包索引) 下载依赖包，请在运行 `install.bat` 脚本前，按以下步骤修改文件：

找到 `install.bat` 文件中以下被注释的行：

```batch
@REM python -m pip install --upgrade pip --proxy=http://127.0.0.1:50470
@REM python -m pip install -r requirements_simple.txt --proxy=http://127.0.0.1:50470
```

取消注释（删除前面的 `@REM `）并将 `50470` 改为您的实际代理端口号：

```batch
python -m pip install --upgrade pip --proxy=http://127.0.0.1:您的端口
python -m pip install -r requirements_simple.txt --proxy=http://127.0.0.1:您的端口
```

## 📁 安装内容

安装完成后，以下主要组件将被安装到您的系统：

-   **MCP 服务器文件**：核心 Python 脚本位于 `%USERPROFILE%\.cursor\cursor-extensions\review-gate-v2\`。
-   **Python 虚拟环境**：在上述 MCP 服务器目录下会创建一个名为 `venv` 的独立 Python 环境，包含所有必需的依赖包。
-   **Cursor 扩展**：Review Gate V2 扩展 (`.vsix` 文件) 将被安装到 Cursor IDE 中。
-   **MCP 配置**：您的 Cursor 配置文件 `%USERPROFILE%\.cursor\mcp.json` 将被自动更新，以注册 Review Gate V2 的 MCP 服务。

## 🧪 测试安装

安装完成后，请按以下步骤验证您的安装是否成功：

1.  **完全重启 Cursor IDE**：这是确保所有配置和扩展生效的关键步骤。
2.  **测试手动触发弹窗**：
    *   在 Cursor IDE 中按下 `Ctrl+Shift+R` 快捷键。
    *   或者，在 Cursor 的 MCP 工具面板中（通常可以在设置或扩展部分找到），找到 `review-gate-v2` 或 `review-gate-v2-fixed` 服务器下的 `review_gate_chat` 工具，并手动点击触发。
    *   确认 Review Gate 弹窗是否正常弹出。
3.  **测试 AI 调用弹窗及消息回传**：
    *   向 Cursor AI 聊天框中输入或语音说：“请使用 review_gate_chat 工具”。
    *   确认 Review Gate 弹窗是否正常弹出，并且您在弹窗中输入的消息能被 AI 正常接收并回显在聊天框中。

## 🎤 语音功能使用

Review Gate V2 支持语音输入转文字 (Speech-to-Text) 功能：

1.  在弹出的 Review Gate 窗口中点击**麦克风图标**。
2.  开始**清晰说话** 2-3 秒（支持中文和英文）。
3.  点击**停止按钮**完成录音。
4.  系统会自动将语音转换为文字并显示在输入框中。

## 📷 图像上传功能

Review Gate V2 支持图像上传，您可以通过图片向 AI 提供视觉信息：

1.  在 Review Gate 窗口中点击**相机图标**。
2.  在文件选择对话框中，选择要上传的图片文件（支持 PNG、JPG、JPEG、GIF、BMP、WebP 等格式）。
3.  图片将作为附件包含在您的反馈中，AI Agent 将能够接收并分析这些图像。

## 🔧 故障排除

### 常见问题

**Q: 安装后无法找到 Review Gate 工具，或者 MCP 服务器显示未连接？**
A: 请确保已**完全重启 Cursor IDE**。检查 Cursor 的扩展面板，确认 Review Gate V2 扩展已正确安装并启用。同时，检查 MCP 工具面板（`Ctrl+Shift+P` -> `MCP Tools`），确认 `review-gate-v2` 和/或 `review-gate-v2-fixed` 服务器已处于“已连接”状态（通常显示为绿色）。如果未连接，请检查日志文件。

**Q: 语音功能不工作，或者无法识别语音？**
A: 确保已安装 **SoX**（Sound eXchange）。您可以在命令行运行 `sox --version` 检查其是否可用。如果未安装，请根据安装步骤中的提示手动从 [SoX 官方网站](http://sox.sourceforge.net/) 下载安装，或如果您的系统安装了 Chocolatey，可以通过 `choco install sox -y` 命令安装。

**Q: MCP 服务器无法启动，或者启动后立即崩溃？**
A: 检查您的 Python 环境是否正确安装（确保是 Python 3.10 或更高版本）。查看**日志文件**了解详细错误信息，通常能提供启动失败的具体原因。常见的错误包括缺少 Python 依赖（运行 `pip install -r requirements_simple.txt` 检查）或端口冲突。

### 日志文件位置

Review Gate V2 MCP 服务器的详细运行日志位于系统临时目录。要查找日志文件，请在 PowerShell 或命令提示符中运行以下命令：

```powershell
python -c "import tempfile; print(tempfile.gettempdir())"
```

然后，导航到该目录，您将找到名为 `review_gate_v2.log` 和 `review_gate_v2_fixed.log` 的文件，它们将包含 MCP 服务器的详细运行日志和任何错误信息，这些信息对于故障排除至关重要。

### 手动安装扩展

如果自动安装扩展失败，您可以尝试手动安装：

1.  打开 Cursor IDE。
2.  按下 `Ctrl+Shift+P` 打开命令面板。
3.  输入并选择 `Extensions: Install from VSIX...`。
4.  在文件选择对话框中，导航到：`%USERPROFILE%\.cursor\cursor-extensions\review-gate-v2\review-gate-v2-2.7.3.vsix`。
5.  点击“确认”进行安装。

## 📝 更新日志

### Windows 11 中文优化版改进

*   ✅ **中文编码修复**：解决了中文编码问题，确保 `mcp.json` 中添加 `"PYTHONIOENCODING":"utf-8"`，并在 `review_gate_v2_mcp_fixed.py` 和 `review_gate_v2_mcp.py` 中强制使用 UTF-8 编码进行文件读写。
*   ✅ **弹窗触发机制优化**：将原版 `_trigger_cursor_popup_immediately` 的更健壮的触发逻辑（包括文件系统同步、多备份触发文件等）移植到 `review_gate_v2_mcp_fixed.py` **并同步回原版 `review_gate_v2_mcp.py`**，确保弹窗稳定弹出。
*   ✅ **消息回传健壮性增强**：**核心修复！** 解决了原版 `review_gate_v2_mcp.py` 弹窗能弹出但无法发送消息的问题，通过将 `fixed` 版中更健壮的 `_wait_for_user_input` 逻辑（包括更宽松的 `trigger_id` 匹配、强制 UTF-8 编码读取和即时文件清理）移植到原版 `review_gate_v2_mcp.py`，确保用户消息能可靠回传。
*   ✅ **Windows 11 兼容性优化**：全面优化脚本和代码，提升在 Windows 11 环境下的运行稳定性。
*   ✅ **中文语音识别支持**：集成了对中文语音的识别支持。
*   ✅ **安装脚本用户友好性改进**：使安装步骤更清晰、更自动化，修复 `install.bat` 中 `mcp.json` `args` 为空的问题。
*   ✅ **增强错误处理和日志记录**：提高了 MCP 服务和安装脚本的错误捕获能力和日志输出，便于问题诊断。

## 🆚 原版与修复版（fixed）核心差异

本项目提供两个 MCP 服务器版本：原版 `review-gate-v2` (对应 `review_gate_v2_mcp.py`) 和修复版 `review-gate-v2-fixed` (对应 `review_gate_v2_mcp_fixed.py`)。主要差异体现在用户输入/消息回传机制上：

*   **原版（`review_gate_v2_mcp.py`）**：
    *   在本次修复前，其 `_wait_for_user_input` 方法对响应文件的 `trigger_id` 匹配要求过于严格。
    *   当响应文件的 `trigger_id` 与预期不符（或为空）时，即使是通用响应，消息也会被忽略，导致“弹窗能弹出但消息发不回来”的问题。
    *   文件读取时未明确指定 `UTF-8` 编码，可能导致中文乱码或解析失败。
*   **修复版（`review_gate_v2_mcp_fixed.py`）**：
    *   对 `trigger_id` 校验更宽松，支持通用 response 文件，即使 `trigger_id` 不完全匹配也能被处理，极大提升了消息回传的成功率。
    *   强制 `UTF-8` 编码读取，避免了中文或特殊字符导致的解析失败。
    *   处理完用户输入后，立即清理 response 文件，防止残留文件影响后续交互。
    *   在**弹窗触发机制**方面，最初的 `fixed` 版也比原版更健壮（此部分逻辑已在本次修复中同步移植回原版）。

**建议：** 如果您在使用原版 `review-gate-v2` 时遇到“弹窗能弹出但消息发不回来”的问题，或者需要更高的稳定性，**推荐使用修复后的原版 `review-gate-v2` 服务**。修复版 `review-gate-v2-fixed` 可作为备选或调试使用。

### 原版 `review_gate_v2_mcp.py` 消息回传修复

**问题：** 原版 `review_gate_v2_mcp.py` 弹窗能正常弹出，但用户在弹窗中输入的消息无法回传到 Cursor AI 聊天框。

**根本原因：**
1.  **严格的 `trigger_id` 校验：** 原版 `_wait_for_user_input` 方法对响应文件的 `trigger_id` 匹配要求过于严格。当响应文件的 `trigger_id` 与预期不符（或为空）时，即使是通用响应，消息也会被忽略。
2.  **编码问题：** 读取响应文件时未明确指定 `UTF-8` 编码，可能导致中文或其他非 ASCII 字符解析失败，使得消息内容为空或乱码。
3.  **文件处理健壮性不足：** 异常处理和文件清理机制不够完善，可能导致文件残留或解析错误中断消息回传。

**修复方案：**
将 `review_gate_v2_mcp_fixed.py` 中更健壮的 `_wait_for_user_input_fixed` 逻辑移植到原版 `review_gate_v2_mcp.py` 的 `_wait_for_user_input` 方法中。具体改进包括：
1.  **更宽松的 `trigger_id` 匹配：** 允许通用响应文件（如 `review_gate_response.json`）即使 `trigger_id` 不完全匹配也能被处理。
2.  **强制 UTF-8 编码读取：** 确保所有响应文件都以 `UTF-8` 编码正确读取。
3.  **即时文件清理：** 处理完响应后立即删除临时文件，防止文件冲突和残留。
4.  **增强错误处理和日志记录：** 提升对 JSON 解析错误和文件操作异常的处理能力和日志可见性。

**结果：** 修复后，原版 `review-gate-v2` 服务已能正常接收并回传弹窗中的用户消息，且其弹窗触发机制也与修复版一样健壮。

## 跨平台差异 (Windows 移植)

本项目在 Windows 环境下进行优化和修复，主要解决了与 macOS/Linux 平台存在的以下差异导致的问题：

### 1. 文件路径分隔符
-   **macOS/Linux**：统一使用 `/` 作为路径分隔符。
-   **Windows**：使用 `\` 作为路径分隔符。在 JSON 配置或跨平台脚本中，需要进行适当转换以确保兼容性。

### 2. 文件编码
-   **macOS/Linux**：默认倾向于使用 `UTF-8` 编码。
-   **Windows**：命令行环境和某些工具可能默认使用本地编码（如 `GBK`/`CP936`）。这导致在文件读写（特别是 JSON 文件）时，如果未明确指定 `UTF-8`，容易出现乱码或解析失败。

### 3. 临时文件处理与文件锁定
-   **macOS/Linux**：对临时文件的创建、读写和删除通常更灵活。
-   **Windows**：对文件的锁定和权限管理可能更严格。频繁或并发的文件操作可能因文件被占用而失败，需要更健壮的重试、同步（如 `os.sync()`）和延迟机制。

### 4. 脚本语言差异
-   **macOS/Linux**：常用的 Shell 脚本（如 Bash）在处理字符串、JSON 和高级逻辑方面更强大和一致。
-   **Windows**：批处理脚本（`.bat`）语法相对简单，处理复杂逻辑和 JSON 结构时，需要更精细的写法来避免错误（例如多行 `echo` 生成 JSON 时的问题）。

**总结：** 这些平台差异可能导致在 macOS/Linux 上运行正常的代码在 Windows 环境下出现意想不到的问题。本项目的修复正是针对这些 Windows 特性进行了优化，以确保其稳定性和兼容性。

## 🙏 致谢

本项目基于 [Lakshman Turlapati](https://github.com/LakshmanTurlapati) 的 [Review-Gate](https://github.com/LakshmanTurlapati/Review-Gate) 项目开发。

感谢原作者的创新想法和开源贡献！

## 📄 许可证

本项目遵循原项目的许可证条款。

---

🎯 **让您的 Cursor AI 请求发挥最大价值，享受深度交互编程体验！** ✨
