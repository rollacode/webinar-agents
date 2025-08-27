"""
Agent Logger for tracking communication between the agent and the game.
Creates session-based log files with sent and answered messages.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class AgentLogger:
    """Logger class for tracking agent communication and actions."""

    def __init__(self, session_name: Optional[str] = None):
        """
        Initialize the logger.

        Args:
            session_name: Optional custom session name. If not provided,
                         will use timestamp-based name.
        """
        self.logs_dir = "logs"
        self.session_name = (
            session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.log_file_path = os.path.join(self.logs_dir, f"{self.session_name}.log")
        self._initialized = False

    def _ensure_logs_directory(self) -> None:
        """Create the logs directory if it doesn't exist."""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            print(f"Created logs directory: {self.logs_dir}")

    def _initialize_log_file(self) -> None:
        """Initialize the log file with session information."""
        if self._initialized:
            return

        # Create logs directory if it doesn't exist
        self._ensure_logs_directory()

        session_info = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat(),
            "log_file": self.log_file_path,
        }

        with open(self.log_file_path, "w", encoding="utf-8") as f:
            f.write("# Agent Session Log\n")
            f.write(f"# Session: {self.session_name}\n")
            f.write(f"# Started: {session_info['start_time']}\n")
            f.write(f"# Log File: {self.log_file_path}\n")
            f.write(f"{'=' * 50}\n\n")

        print(f"Initialized log file: {self.log_file_path}")
        self._initialized = True

    def log_sent(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a message sent to the agent.

        Args:
            message: The message sent to the agent
            context: Optional context information (e.g., game state, action type)
        """
        self._initialize_log_file()

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] SENT:\n")
            f.write(f"{message}\n")

            if context:
                f.write(
                    f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}\n"
                )

            f.write(f"{'-' * 30}\n")

    def log_answered(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        self._initialize_log_file()

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] LLM RESPONSE:\n")
            f.write(f"{response}\n")

            if context:
                f.write(
                    f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}\n"
                )

            f.write(f"{'-' * 30}\n")

    def log_action(
        self,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an action taken by the agent.

        Args:
            action: The action name
            parameters: Action parameters
            result: Action result
        """
        self._initialize_log_file()

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ACTION: {action}\n")

            if parameters:
                f.write(
                    f"Parameters: {json.dumps(parameters, indent=2, ensure_ascii=False)}\n"
                )

            if result:
                f.write(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}\n")

            f.write(f"{'-' * 30}\n")

    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error that occurred.

        Args:
            error: Error message
            context: Optional context information
        """
        self._initialize_log_file()

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ERROR:\n")
            f.write(f"{error}\n")

            if context:
                f.write(
                    f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}\n"
                )

            f.write(f"{'-' * 30}\n")

    def log_info(self, info: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log informational message.

        Args:
            info: Information message
            context: Optional context information
        """
        self._initialize_log_file()

        timestamp = datetime.now().strftime("%H:%M:%S")

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] INFO:\n")
            f.write(f"{info}\n")

            if context:
                f.write(
                    f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}\n"
                )

            f.write(f"{'-' * 30}\n")

    def close_session(self) -> None:
        """Close the session and log final information."""
        if not self._initialized:
            return

        end_time = datetime.now().isoformat()

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 50}\n")
            f.write(f"# Session ended: {end_time}\n")
            f.write(f"# Total duration: {self._get_session_duration()}\n")

        print(f"Session log completed: {self.log_file_path}")

    def _get_session_duration(self) -> str:
        """Calculate session duration."""
        # This would need to be implemented based on when the session started
        # For now, return a placeholder
        return "Duration not tracked"

    def get_log_file_path(self) -> str:
        """Get the current log file path."""
        return self.log_file_path
