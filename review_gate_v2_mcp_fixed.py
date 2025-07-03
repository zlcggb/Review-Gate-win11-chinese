#!/usr/bin/env python3
"""
Review Gate 2.0 - Fixed Version MCP Server with Cursor Integration
修复版本：解决编码问题和trigger ID匹配问题
Author: Lakshman Turlapati (Modified for fixes)
"""

import asyncio
import json
import sys
import logging
import os
import time
import uuid
import glob
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

# Speech-to-text imports
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    TextContent,
    Tool,
    CallToolResult,
    Resource,
    ImageContent,
    EmbeddedResource,
)

def get_temp_path(filename: str) -> str:
    """Get cross-platform temporary file path"""
    if os.name == 'nt':  # Windows
        temp_dir = tempfile.gettempdir()
    else:  # macOS and Linux
        temp_dir = '/tmp'
    return os.path.join(temp_dir, filename)

# Configure logging
log_file_path = get_temp_path('review_gate_v2_fixed.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class ReviewGateServerFixed:
    def __init__(self):
        self.server = Server("review-gate-v2-fixed")
        self.setup_handlers()
        self.shutdown_requested = False
        self.shutdown_reason = ""
        self._last_attachments = []
        
        logger.info("🚀 Review Gate 2.0 FIXED server initialized")

    def setup_handlers(self):
        """Set up MCP request handlers"""
        
        @self.server.list_tools()
        async def list_tools():
            tools = [
                Tool(
                    name="review_gate_chat",
                    description="Open Review Gate chat popup in Cursor for feedback and reviews",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to display in the Review Gate popup",
                                "default": "Please provide your review or feedback:"
                            },
                            "title": {
                                "type": "string", 
                                "description": "Title for the Review Gate popup window",
                                "default": "Review Gate V2 - Fixed"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context",
                                "default": ""
                            },
                            "urgent": {
                                "type": "boolean",
                                "description": "Whether this is urgent",
                                "default": False
                            }
                        }
                    }
                )
            ]
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            logger.info(f"🎯 TOOL CALLED: {name}")
            logger.info(f"📋 Arguments: {arguments}")
            
            try:
                if name == "review_gate_chat":
                    return await self._handle_review_gate_chat_fixed(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"💥 Tool error: {e}")
                return [TextContent(type="text", text=f"ERROR: {str(e)}")]

    async def _handle_review_gate_chat_fixed(self, args: dict) -> list[TextContent]:
        """修复版本的Review Gate chat处理"""
        message = args.get("message", "Please provide your review or feedback:")
        title = args.get("title", "Review Gate V2 - Fixed")
        context = args.get("context", "")
        urgent = args.get("urgent", False)
        
        logger.info(f"💬 ACTIVATING Review Gate chat (FIXED VERSION)")
        logger.info(f"📝 Message: {message}")
        
        # 创建触发文件
        trigger_id = f"review_{int(time.time() * 1000)}"
        
        success = await self._trigger_cursor_popup_fixed({
            "tool": "review_gate_chat",
            "message": message,
            "title": title,
            "context": context,
            "urgent": urgent,
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "immediate_activation": True
        })
        
        if success:
            logger.info(f"🔥 POPUP TRIGGERED - waiting for user input (trigger_id: {trigger_id})")
            
            # 等待用户输入（修复版本）
            user_input = await self._wait_for_user_input_fixed(trigger_id, timeout=300)
            
            if user_input:
                logger.info(f"✅ RECEIVED USER INPUT: {user_input[:100]}...")
                return [TextContent(type="text", text=f"User Response: {user_input}")]
            else:
                return [TextContent(type="text", text="TIMEOUT: No user input received within 5 minutes")]
        else:
            return [TextContent(type="text", text="ERROR: Failed to trigger popup")]

    async def _wait_for_user_input_fixed(self, trigger_id: str, timeout: int = 300) -> Optional[str]:
        """修复版本的用户输入等待方法"""
        response_patterns = [
            Path(get_temp_path(f"review_gate_response_{trigger_id}.json")),
            Path(get_temp_path("review_gate_response.json")),  # 通用响应文件
            Path(get_temp_path(f"mcp_response_{trigger_id}.json")),
            Path(get_temp_path("mcp_response.json"))
        ]
        
        logger.info(f"👁️ 监控响应文件: {[str(p) for p in response_patterns]}")
        logger.info(f"🔍 等待的Trigger ID: {trigger_id}")
        
        start_time = time.time()
        check_interval = 0.5  # 每500ms检查一次
        
        while time.time() - start_time < timeout:
            try:
                for response_file in response_patterns:
                    if response_file.exists():
                        try:
                            # 修复：指定UTF-8编码读取文件
                            with open(response_file, 'r', encoding='utf-8') as f:
                                file_content = f.read().strip()
                            
                            logger.info(f"📄 发现响应文件 {response_file.name}: {file_content[:200]}...")
                            
                            if file_content.startswith('{'):
                                data = json.loads(file_content)
                                user_input = data.get("user_input", data.get("response", data.get("message", ""))).strip()
                                
                                # 修复：更宽松的trigger ID匹配
                                response_trigger_id = data.get("trigger_id", "")
                                if response_trigger_id:
                                    # 检查trigger ID是否匹配或者是否为通用响应
                                    if response_trigger_id != trigger_id and response_file.name != "review_gate_response.json":
                                        logger.info(f"⚠️ Trigger ID不匹配，但继续处理: expected {trigger_id}, got {response_trigger_id}")
                                        # 不跳过，继续处理
                                
                                # 处理附件
                                attachments = data.get("attachments", [])
                                if attachments:
                                    self._last_attachments = attachments
                                    logger.info(f"📎 发现 {len(attachments)} 个附件")
                            else:
                                user_input = file_content
                                self._last_attachments = []
                            
                            # 立即清理响应文件
                            try:
                                response_file.unlink()
                                logger.info(f"🧹 响应文件已清理: {response_file.name}")
                            except Exception as cleanup_error:
                                logger.warning(f"⚠️ 清理错误: {cleanup_error}")
                            
                            if user_input:
                                logger.info(f"🎉 成功接收用户输入: {user_input[:100]}...")
                                return user_input
                            else:
                                logger.warning(f"⚠️ 文件中用户输入为空: {response_file.name}")
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON解析错误 {response_file.name}: {e}")
                            # 尝试删除损坏的文件
                            try:
                                response_file.unlink()
                            except:
                                pass
                        except Exception as e:
                            logger.error(f"❌ 处理响应文件错误 {response_file.name}: {e}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ 等待循环错误: {e}")
                await asyncio.sleep(1)
        
        logger.warning(f"⏰ 等待用户输入超时 (trigger_id: {trigger_id})")
        return None

    async def _trigger_cursor_popup_fixed(self, data: dict) -> bool:
        """修复版本的弹窗触发方法"""
        try:
            trigger_file = Path(get_temp_path("review_gate_trigger.json"))
            
            trigger_data = {
                "timestamp": datetime.now().isoformat(),
                "system": "review-gate-v2-fixed",
                "editor": "cursor",
                "data": data,
                "pid": os.getpid(),
                "active_window": True,
                "mcp_integration": True,
                "immediate_activation": True
            }
            
            logger.info(f"🎯 创建触发文件: {trigger_file}")
            
            # 修复：指定UTF-8编码写入文件
            with open(trigger_file, 'w', encoding='utf-8') as f:
                json.dump(trigger_data, f, indent=2, ensure_ascii=False)
            
            if not trigger_file.exists():
                logger.error(f"❌ 创建触发文件失败: {trigger_file}")
                return False
            
            file_size = trigger_file.stat().st_size
            logger.info(f"🔥 触发文件已创建: {trigger_file} ({file_size} bytes)")
            
            # 添加延迟让扩展处理
            await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建触发文件失败: {e}")
            return False

    async def run(self):
        """运行修复版本的服务器"""
        logger.info("🚀 启动Review Gate 2.0 FIXED MCP服务器...")
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ Review Gate v2 FIXED服务器在stdio传输上激活")
            
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """主入口点"""
    logger.info("🎬 启动Review Gate v2 FIXED MCP服务器...")
    
    try:
        server = ReviewGateServerFixed()
        await server.run()
    except Exception as e:
        logger.error(f"❌ MCP服务器严重错误: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 服务器被用户停止")
    except Exception as e:
        logger.error(f"❌ 服务器崩溃: {e}")
        sys.exit(1) 