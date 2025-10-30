import os
import base64
import json
from pathlib import Path

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code repo
# and add the `decky-loader/plugin/imports` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky
import asyncio

try:
    from openai import AsyncOpenAI
    from PIL import Image
    import io
except ImportError as e:
    decky.logger.error(f"Failed to import required libraries: {e}")
    AsyncOpenAI = None
    Image = None

class Plugin:
    def __init__(self):
        self.openai_client = None
        self.api_key = None
        
    # A normal method. It can be called from the TypeScript side using @decky/api.
    async def add(self, left: int, right: int) -> int:
        return left + right

    async def long_running(self):
        await asyncio.sleep(15)
        # Passing through a bunch of random data, just as an example
        await decky.emit("timer_event", "Hello from the backend!", True, 2)
    
    async def set_api_key(self, api_key: str) -> bool:
        """Set the OpenAI API key and save it to settings."""
        try:
            self.api_key = api_key
            if AsyncOpenAI:
                self.openai_client = AsyncOpenAI(api_key=api_key)
            
            # Save the API key to settings
            settings_path = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "settings.json"
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump({"api_key": api_key}, f)
            
            decky.logger.info("API key saved successfully")
            return True
        except Exception as e:
            decky.logger.error(f"Failed to set API key: {e}")
            return False
    
    async def get_api_key(self) -> str:
        """Get the stored OpenAI API key."""
        try:
            settings_path = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "settings.json"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get("api_key", "")
            return ""
        except Exception as e:
            decky.logger.error(f"Failed to get API key: {e}")
            return ""
    
    async def capture_screenshot(self) -> str:
        """Capture a screenshot and return it as base64 encoded string."""
        try:
            # Try to find a recent Steam screenshot
            # Steam Deck stores screenshots in various locations
            screenshot_paths = [
                Path(decky.DECKY_USER_HOME) / ".steam" / "steam" / "screenshots",
                Path(decky.DECKY_USER_HOME) / ".local" / "share" / "Steam" / "screenshots",
            ]
            
            latest_screenshot = None
            latest_time = 0
            
            for screenshot_dir in screenshot_paths:
                if screenshot_dir.exists():
                    for screenshot_file in screenshot_dir.rglob("*.jpg"):
                        mtime = screenshot_file.stat().st_mtime
                        if mtime > latest_time:
                            latest_time = mtime
                            latest_screenshot = screenshot_file
            
            if latest_screenshot and Image:
                # Read and encode the screenshot
                with Image.open(latest_screenshot) as img:
                    # Resize if too large to save on API costs
                    max_size = (1024, 1024)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Convert to base64
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    img_bytes = buffer.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    
                    decky.logger.info(f"Screenshot captured: {latest_screenshot}")
                    return img_base64
            
            # If no screenshot found, try using X11 screenshot (fallback)
            decky.logger.warning("No recent Steam screenshot found, trying X11 screenshot")
            
            # Use xwd to capture the screen (if available)
            import subprocess
            try:
                # Get the DISPLAY environment variable
                display = os.environ.get('DISPLAY', ':0')
                
                # Capture using import from ImageMagick or xwd
                result = subprocess.run(
                    ['import', '-window', 'root', '-'],
                    capture_output=True,
                    timeout=5,
                    env={**os.environ, 'DISPLAY': display}
                )
                
                if result.returncode == 0 and Image:
                    img = Image.open(io.BytesIO(result.stdout))
                    max_size = (1024, 1024)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    img_bytes = buffer.getvalue()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    
                    decky.logger.info("Screenshot captured using X11")
                    return img_base64
            except Exception as e:
                decky.logger.error(f"Failed to capture X11 screenshot: {e}")
            
            return ""
        except Exception as e:
            decky.logger.error(f"Failed to capture screenshot: {e}")
            return ""
    
    async def get_quest_help(self, screenshot_base64: str) -> dict:
        """Send screenshot to OpenAI for quest help analysis."""
        try:
            if not self.openai_client:
                # Try to load API key if not already loaded
                api_key = await self.get_api_key()
                if api_key and AsyncOpenAI:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                    self.api_key = api_key
                else:
                    return {
                        "success": False,
                        "error": "OpenAI API key not configured. Please set your API key first."
                    }
            
            if not screenshot_base64:
                return {
                    "success": False,
                    "error": "No screenshot available. Please take a screenshot first."
                }
            
            # Prepare the message for OpenAI
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I'm stuck in this game and need help with what to do next. Please analyze this screenshot and provide clear, step-by-step guidance on how to proceed. Focus on: 1) What quest or objective I'm currently on, 2) What I should do next to progress, 3) Any important details or hints visible in the screenshot."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{screenshot_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call OpenAI API
            decky.logger.info("Calling OpenAI API for quest help...")
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",  # Using gpt-4-turbo which supports vision
                messages=messages,
                max_tokens=500
            )
            
            help_text = response.choices[0].message.content
            decky.logger.info(f"Received response from OpenAI: {help_text[:100]}...")
            
            return {
                "success": True,
                "help_text": help_text
            }
        except Exception as e:
            error_msg = str(e)
            decky.logger.error(f"Failed to get quest help: {error_msg}")
            return {
                "success": False,
                "error": f"Failed to get help from AI: {error_msg}"
            }
    
    async def request_quest_help(self) -> dict:
        """Main method to request quest help - captures screenshot and gets AI help."""
        try:
            # Capture screenshot
            screenshot_base64 = await self.capture_screenshot()
            
            if not screenshot_base64:
                return {
                    "success": False,
                    "error": "Failed to capture screenshot. Please ensure you have taken a screenshot recently."
                }
            
            # Get help from OpenAI
            result = await self.get_quest_help(screenshot_base64)
            return result
            
        except Exception as e:
            error_msg = str(e)
            decky.logger.error(f"Failed to request quest help: {error_msg}")
            return {
                "success": False,
                "error": f"An error occurred: {error_msg}"
            }

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        self.loop = asyncio.get_event_loop()
        decky.logger.info("Quest Helper Plugin Starting!")
        
        # Try to load saved API key
        api_key = await self.get_api_key()
        if api_key and AsyncOpenAI:
            self.openai_client = AsyncOpenAI(api_key=api_key)
            self.api_key = api_key
            decky.logger.info("API key loaded from settings")

    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        decky.logger.info("Goodnight World!")
        pass

    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        decky.logger.info("Goodbye World!")
        pass

    async def start_timer(self):
        self.loop.create_task(self.long_running())

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky.decky_LOG_DIR/template.log`
        decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky.decky_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.decky_SETTINGS_DIR/`
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        decky.migrate_runtime(
            os.path.join(decky.DECKY_HOME, "template"),
            os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))
