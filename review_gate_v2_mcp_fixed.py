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

# MCP Server for Review Gate V2 - Fixed Version
# This server handles communication between Cursor IDE and AI Agent for interactive reviews.
# 
# **Recent Improvement:** This project now includes an enhanced `install.bat` script that intelligently merges `mcp.json` configurations.
# Instead of overwriting, it safely adds Review Gate's MCP services to your existing `mcp.json` file, preserving your other MCP configurations.

import asyncio
import json
import logging
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import whisper
from mcp.server import stdio_server
from mcp.models import TextContent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_temp_path(filename: str) -> str:
    """Get a temporary file path suitable for the OS."""
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))
    if not os.path.exists(temp_dir):
        temp_dir = "/tmp" # Fallback for non-existent temp dir
    return os.path.join(temp_dir, filename)

class ReviewGateServerFixed:
    def __init__(self):
        self.server = stdio_server()
        self.setup_handlers()
        self.whisper_model = None
        self.speech_monitoring_thread = None
        self.speech_monitoring_active = False
        self._last_attachments = [] # Store last attachments from user input
        
        # Initialize Whisper model in a separate thread/process to avoid blocking startup
        # self._initialize_whisper_model() # Disabled for stability

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            logger.info("List tools requested")
            return [
                {
                    "name": "review_gate_chat",
                    "description": "Open Review Gate chat popup in Cursor for feedback and reviews",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to display in the Review Gate popup"},
                            "title": {"type": "string", "description": "Title for the Review Gate popup window"},
                            "context": {"type": "string", "description": "Additional context about what needs review"},
                            "urgent": {"type": "boolean", "description": "Whether this is an urgent review request"},
                        },
                        "required": ["message"],
                    },
                },
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            logger.info(f"Call tool requested: {name} with args {arguments}")
            if name == "review_gate_chat":
                return await self._handle_review_gate_chat_fixed(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_review_gate_chat_fixed(self, args: dict) -> list[TextContent]:
        message = args.get("message", "")
        title = args.get("title", "Review Gate")
        context = args.get("context", "")
        urgent = args.get("urgent", False)
        
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
                                
                                # 修复：更严格的trigger ID匹配，避免读取旧消息和不相关的通用响应
                                response_trigger_id = data.get("trigger_id", "")
                                if response_trigger_id and response_trigger_id != trigger_id:
                                    logger.warning(f"⚠️ 发现不匹配的Trigger ID ({response_trigger_id})，预期为({trigger_id})。跳过此响应文件: {response_file.name}")
                                    # 立即清理不匹配的响应文件，避免再次被读取
                                    try:
                                        response_file.unlink()
                                        logger.info(f"🧹 已清理不匹配的响应文件: {response_file.name}")
                                    except Exception as cleanup_error:
                                        logger.warning(f"⚠️ 清理不匹配响应文件错误: {cleanup_error}")
                                    continue # 跳过当前文件，检查下一个

                                # 如果走到这里，说明response_trigger_id匹配，或者响应文件不包含trigger_id（视为通用响应）。
                                # 此时，我们继续处理文件内容。

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
        """Create trigger file for Cursor extension with immediate activation and enhanced debugging (from original)"""
        try:
            # Add delay before creating trigger to ensure readiness
            await asyncio.sleep(0.1)  # Wait 100ms before trigger creation
            
            trigger_file = Path(get_temp_path("review_gate_trigger.json"))
            
            trigger_data = {
                "timestamp": datetime.now().isoformat(),
                "system": "review-gate-v2",
                "editor": "cursor",
                "data": data,
                "pid": os.getpid(),
                "active_window": True,
                "mcp_integration": True,
                "immediate_activation": True
            }
            
            logger.info(f"🎯 CREATING trigger file with data: {json.dumps(trigger_data, indent=2)}")
            
            # Write trigger file with immediate flush
            trigger_file.write_text(json.dumps(trigger_data, indent=2))
            
            # Verify file was written successfully
            if not trigger_file.exists():
                logger.error(f"❌ Failed to create trigger file: {trigger_file}")
                return False
                
            try:
                file_size = trigger_file.stat().st_size
                if file_size == 0:
                    logger.error(f"❌ Trigger file is empty: {trigger_file}")
                    return False
            except FileNotFoundError:
                # File may have been consumed by the extension already - this is OK
                logger.info(f"✅ Trigger file was consumed immediately by extension: {trigger_file}")
                file_size = len(json.dumps(trigger_data, indent=2))
            
            # Force file system sync with retry
            for attempt in range(3):
                try:
                    os.sync()
                    break
                except Exception as sync_error:
                    logger.warning(f"⚠️ Sync attempt {attempt + 1} failed: {sync_error}")
                    await asyncio.sleep(0.1)  # Wait 100ms between attempts
            
            logger.info(f"🔥 IMMEDIATE trigger created for Cursor: {trigger_file}")
            logger.info(f"📁 Trigger file path: {trigger_file.absolute()}")
            logger.info(f"📊 Trigger file size: {file_size} bytes")
            
            # Create multiple backup trigger files for reliability
            await self._create_backup_triggers_fixed(data)
            
            # Add small delay to allow extension to process
            await asyncio.sleep(0.2)  # Wait 200ms for extension to process
            
            # Note: Trigger file may have been consumed by extension already, which is good!
            try:
                if trigger_file.exists():
                    logger.info(f"✅ Trigger file still exists: {trigger_file}")
                else:
                    logger.info(f"✅ Trigger file was consumed by extension: {trigger_file}")
                    logger.info(f"🎯 This is expected behavior - extension is working properly")
            except Exception as check_error:
                logger.info(f"✅ Cannot check trigger file status (likely consumed): {check_error}")
                logger.info(f"🎯 This is expected behavior - extension is working properly")
            
            # Check if extension might be watching
            log_file = Path(get_temp_path("review_gate_v2.log"))
            if log_file.exists():
                logger.info(f"📝 MCP log file exists: {log_file}")
            else:
                logger.warning(f"⚠️ MCP log file missing: {log_file}")
            
            # Force log flush
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to create Review Gate trigger: {e}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            # Wait before returning failure
            await asyncio.sleep(1.0)  # Wait 1 second before confirming failure
            return False

    async def _create_backup_triggers_fixed(self, data: dict):
        """Create backup trigger files for better reliability (from original)"""
        try:
            # Create multiple backup trigger files
            for i in range(3):
                backup_trigger = Path(get_temp_path(f"review_gate_trigger_{i}.json"))
                backup_data = {
                    "backup_id": i,
                    "timestamp": datetime.now().isoformat(),
                    "system": "review-gate-v2",
                    "data": data,
                    "mcp_integration": True,
                    "immediate_activation": True
                }
                backup_trigger.write_text(json.dumps(backup_data, indent=2))
            
            logger.info("🔄 Backup trigger files created for reliability")
            
        except Exception as e:
            logger.warning(f"⚠️ Backup trigger creation failed: {e}")

    # def _initialize_whisper_model(self): # Original, re-enabled after fixing
    #     """Initialize the Whisper model for speech-to-text functionality."""
    #     logger.info("Attempting to initialize Whisper model...")
    #     try:
    #         self.whisper_model = whisper.load_model("base")
    #         logger.info("✅ Whisper model loaded successfully.")
    #     except Exception as e:
    #         logger.error(f"❌ Failed to load Whisper model: {e}")
    #         logger.error("Speech-to-text functionality will be disabled.")
    #         self.whisper_model = None
    
    # Removed _start_speech_monitoring as well, for stability reasons
    
    # def _start_speech_monitoring(self): # Original, re-enabled after fixing
    #     """Start a background thread to monitor for speech trigger files."""
    #     if not self.whisper_model:
    #         logger.warning("Speech model not loaded, skipping speech monitoring startup.")
    #         return
    #     
    #     logger.info("Starting speech monitoring thread...")
    #     if self.speech_monitoring_thread and self.speech_monitoring_thread.is_alive():
    #         logger.info("Speech monitoring thread already running.")
    #         return
    #     
    #     # Capture self for use in the thread function
    #     server_instance = self
    #     
    #     def monitor_speech_triggers():
    #         speech_trigger_file = Path(get_temp_path("review_gate_speech_trigger.json"))
    #         
    #         logger.info(f"Speech monitoring thread started. Watching: {speech_trigger_file}")
    #         
    #         while server_instance.speech_monitoring_active:
    #             try:
    #                 if speech_trigger_file.exists():
    #                     logger.info(f"Speech trigger file found: {speech_trigger_file}")
    #                     try:
    #                         with open(speech_trigger_file, 'r', encoding='utf-8') as f:
    #                             trigger_data = json.loads(f.read())
    #                         server_instance._process_speech_request(trigger_data)
    #                         # Clean up trigger file after processing
    #                         speech_trigger_file.unlink()
    #                         logger.info(f"Speech trigger file cleaned up: {speech_trigger_file}")
    #                     except json.JSONDecodeError as e:
    #                         logger.error(f"Error decoding speech trigger JSON: {e}")
    #                     except Exception as e:
    #                         logger.error(f"Error processing speech trigger: {e}")
    #                 
    #                 time.sleep(0.5) # Check every 500ms
    #             except Exception as e:
    #                 logger.error(f"Error in speech monitoring loop: {e}")
    #                 time.sleep(1) # Wait longer on error
    #         logger.info("Speech monitoring thread stopped.")
    # 
    #     self.speech_monitoring_active = True
    #     self.speech_monitoring_thread = threading.Thread(target=monitor_speech_triggers, daemon=True)
    #     self.speech_monitoring_thread.start()

    # def _process_speech_request(self, trigger_data):
    #     """Process a speech request from the extension."""
    #     trigger_id = trigger_data.get("trigger_id")
    #     audio_file_path = trigger_data.get("audio_file_path")
    #     
    #     if not trigger_id or not audio_file_path:
    #         logger.error("Invalid speech trigger data.")
    #         return
    #     
    #     logger.info(f"Processing speech request for trigger {trigger_id} from {audio_file_path}")
    #     
    #     try:
    #         if not os.path.exists(audio_file_path):
    #             logger.error(f"Audio file not found: {audio_file_path}")
    #             self._write_speech_response(trigger_id, None, error="Audio file not found.")
    #             return
    #             
    #         # Transcribe audio
    #         logger.info("Starting Whisper transcription...")
    #         # Load audio and pad/trim it to 30 seconds
    #         audio = whisper.load_audio(audio_file_path)
    #         audio = whisper.pad_or_trim(audio)
    #         
    #         # Make a log-Mel spectrogram and move to the same device as the model
    #         mel = whisper.log_mel_spectrogram(audio, self.whisper_model.n_mels).to(self.whisper_model.device)
    #         
    #         # Detect the spoken language
    #         _, probs = self.whisper_model.detect_language(mel)
    #         detected_language = max(probs, key=probs.get)
    #         logger.info(f"Detected language: {detected_language}")
    #         
    #         # Decode the audio
    #         options = whisper.DecodingOptions(language=detected_language, fp16=False) # fp16=False for CPU or older GPUs
    #         result = whisper.decode(self.whisper_model, mel, options)
    #         
    #         transcription = result.text
    #         logger.info(f"Transcription for {trigger_id}: {transcription[:100]}...")
    #         self._write_speech_response(trigger_id, transcription)
    #         
    #     except Exception as e:
    #         logger.error(f"Error during speech processing for {trigger_id}: {e}")
    #         import traceback
    #         logger.error(f"Full traceback: {traceback.format_exc()}")
    #         self._write_speech_response(trigger_id, None, error=f"Speech processing error: {e}")
    #     finally:
    #         # Clean up audio file
    #         if os.path.exists(audio_file_path):
    #             try:
    #                 os.unlink(audio_file_path)
    #                 logger.info(f"Cleaned up audio file: {audio_file_path}")
    #             except Exception as e:
    #                 logger.warning(f"Failed to clean up audio file {audio_file_path}: {e}")

    # def _write_speech_response(self, trigger_id, transcription, error=None):
    #     """Write the speech transcription or error to a response file."""
    #     speech_response_file = Path(get_temp_path(f"review_gate_speech_response_{trigger_id}.json"))
    #     
    #     response_data = {
    #         "trigger_id": trigger_id,
    #         "transcription": transcription,
    #         "error": error,
    #         "timestamp": datetime.now().isoformat()
    #     }
    #     
    #     try:
    #         speech_response_file.write_text(json.dumps(response_data, indent=2), encoding='utf-8')
    #         logger.info(f"Speech response written to: {speech_response_file}")
    #     except Exception as e:
    #         logger.error(f"Failed to write speech response for {trigger_id}: {e}")

    # def get_speech_monitoring_status(self):
    #     """Return the status of the speech monitoring thread."""
    #     return {
    #         "active": self.speech_monitoring_active,
    #         "thread_alive": self.speech_monitoring_thread and self.speech_monitoring_thread.is_alive()
    #     }

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