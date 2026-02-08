from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..mcp.task_tools import TaskTools
from ..mcp.identity_tool import IdentityTool
from ..models.conversation import Conversation
from ..models.message import Message

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class ChatAgent:
    """
    Chat agent that processes user messages,
    executes backend tools, and returns natural language responses.
    """

    def __init__(self):
        self.cohere_client = None
        self._initialize_cohere()

    def _initialize_cohere(self):
        try:
            import cohere
            api_key = os.getenv("COHERE_API_KEY")
            if not api_key:
                raise ValueError("COHERE_API_KEY is not set")
            self.cohere_client = cohere.AsyncClient(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Cohere init failed: {str(e)}")

    # -----------------------------
    # Conversation helpers
    # -----------------------------

    async def _create_or_get_conversation(
        self, session: AsyncSession, conversation_id: Optional[str], user_id: str
    ) -> str:
        if conversation_id:
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await session.exec(stmt)
            if result.first():
                return conversation_id

        convo = Conversation(
            user_id=user_id,
            title="AI Chat Session",
            is_active=True
        )
        session.add(convo)
        await session.commit()
        await session.refresh(convo)
        return convo.id

    async def _save_message(
        self,
        session: AsyncSession,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str
    ):
        msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(msg)
        await session.commit()

    async def _get_conversation_history(
        self, session: AsyncSession, conversation_id: str
    ) -> List[Dict[str, str]]:
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc())

        result = await session.exec(stmt)
        messages = result.all()

        history = []
        for msg in messages:
            history.append({
                "role": "USER" if msg.role == "user" else "CHATBOT",
                "message": msg.content
            })

        return history

    # -----------------------------
    # Intent detection (backend)
    # -----------------------------

    def _detect_intent(self, message: str) -> Optional[str]:
        msg = message.lower()

        if any(w in msg for w in ["add", "create", "new task"]):
            return "add_task"
        if any(w in msg for w in ["delete", "remove"]):
            return "delete_task"
        if any(w in msg for w in ["complete", "done", "finish"]):
            return "complete_task"
        if any(w in msg for w in ["list", "show", "tasks"]):
            return "list_tasks"
        if any(w in msg for w in ["who am i", "my email"]):
            return "get_current_user"

        return None

    # -----------------------------
    # Helper methods
    # -----------------------------

    def _extract_task_info(self, message: str, intent: str) -> str:
        """Extract relevant information from the user message based on intent."""
        message_lower = message.lower()

        # For add_task, extract the task title
        if intent == "add_task":
            # Look for keywords that might indicate the task title
            for separator in ['"','\'', 'task', 'for me', 'me', 'to']:
                if separator in message:
                    # Extract content after the separator
                    parts = message.split(separator, 1)
                    if len(parts) > 1:
                        title = parts[1].strip().strip('"').strip("'")
                        if title:
                            return title

        # For delete_task and complete_task, try to extract task ID or title
        elif intent in ["delete_task", "complete_task"]:
            # Look for identifiers like numbers or quoted text
            import re
            # Try to extract a number (potential task ID)
            number_match = re.search(r'\b(\d+)\b', message)
            if number_match:
                return number_match.group(1)

            # Try to extract quoted text (potential task title)
            quote_match = re.search(r'["\']([^"\']+)["\']', message)
            if quote_match:
                return quote_match.group(1)

        # If no specific extraction, return the cleaned message
        return message.strip()

    # -----------------------------
    # Tool execution
    # -----------------------------

    async def _execute_tool(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
        tool: str,
        message: str
    ) -> Any:
        if tool == "add_task":
            return await TaskTools.add_task(
                session=session,
                user_id=user_id,
                title=message
            )

        if tool == "list_tasks":
            return await TaskTools.list_tasks(
                session=session,
                user_id=user_id
            )

        if tool == "complete_task":
            # Try to interpret the message as either a task ID or title
            task_id = message
            # If it's not a numeric ID, we might need to look up by title
            # For now, assuming it's an ID
            return await TaskTools.complete_task(
                session=session,
                user_id=user_id,
                task_id=task_id
            )

        if tool == "delete_task":
            # Try to interpret the message as either a task ID or title
            task_id = message
            return await TaskTools.delete_task(
                session=session,
                user_id=user_id,
                task_id=task_id
            )

        if tool == "get_current_user":
            return await IdentityTool.get_current_user(user_id, email)

        raise ValueError("Unknown tool")

    # -----------------------------
    # AI Response Processing
    # -----------------------------

    async def _process_ai_response_for_tools(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
        ai_response: str,
        history: List[Dict[str, str]]
    ) -> str:
        """Process AI response to extract and execute any JSON tool calls."""
        import re
        import json

        processed_response = ai_response
        tools_executed = False

        # First, look for JSON in markdown code blocks (```json ... ``` or ```)
        # Find all occurrences of ```json or ``` followed by content and ending with ```
        start_marker = "```"
        end_marker = "```"

        pos = 0
        while pos < len(processed_response):
            start_pos = processed_response.find(start_marker, pos)
            if start_pos == -1:
                break

            # Look for the end of the opening marker
            opening_end = processed_response.find("\n", start_pos)
            if opening_end == -1:
                break

            # Find the closing ```
            end_pos = processed_response.find(end_marker, opening_end + 1)
            if end_pos == -1:
                break

            # Extract the content between the markers
            json_content = processed_response[opening_end + 1:end_pos].strip()

            # Try to parse as JSON
            try:
                parsed_json = json.loads(json_content)
                # Check if this looks like a tool call
                if isinstance(parsed_json, dict) and "tool" in parsed_json and "params" in parsed_json:
                    tool_call = parsed_json

                    # Execute the tool call
                    result = await self._execute_tool_from_params(
                        session, user_id, email, tool_call["tool"], tool_call["params"]
                    )

                    # Update the response to include the result of the tool execution
                    # For now, we'll remove the JSON block since the tool was executed
                    full_block = processed_response[start_pos:end_pos + 3]
                    processed_response = processed_response.replace(full_block, "").strip()
                    tools_executed = True

                    # Optionally, we can add a confirmation message to the user
                    if tool_call["tool"] == "add_task" and "title" in tool_call["params"]:
                        processed_response += f"\n\nI've added '{tool_call['params']['title']}' to your tasks."
                    elif tool_call["tool"] == "delete_task":
                        processed_response += f"\n\nI've deleted the task as requested."
                    elif tool_call["tool"] == "complete_task":
                        processed_response += f"\n\nI've marked the task as completed."
                    elif tool_call["tool"] == "list_tasks":
                        processed_response += f"\n\nHere are your tasks: {result}"

                    # Continue processing from the beginning as the string has changed
                    pos = 0
                    continue
            except json.JSONDecodeError:
                # Not valid JSON, continue searching
                pass

            pos = end_pos + 3

        # After processing markdown code blocks, look for standalone JSON objects
        # Use a more comprehensive approach to find JSON objects that might be standalone
        # This handles cases like the one in the logs: '{\n  "tool": "add_task", ...}'

        # Find all potential JSON objects that start with {"tool": pattern
        # We'll use a different approach - look for patterns that look like JSON tool calls
        import re

        # Look for JSON objects that contain tool calls, accounting for newlines and formatting
        # This will find both compact and multi-line JSON objects
        json_pattern = r'\{\s*["\']tool["\']\s*:\s*["\'][^"\']*["\']\s*,\s*["\']params["\']\s*:'

        # Find starting positions of potential JSON objects
        start_positions = [m.start() for m in re.finditer(json_pattern, processed_response)]

        for start_pos in reversed(start_positions):  # Process in reverse to not mess up indices
            # Try to extract the complete JSON object starting from this position
            json_obj, end_pos = self._extract_json_object(processed_response, start_pos)

            if json_obj:
                try:
                    parsed_json = json.loads(json_obj)
                    # Check if this looks like a tool call
                    if isinstance(parsed_json, dict) and "tool" in parsed_json and "params" in parsed_json:
                        tool_call = parsed_json

                        # Execute the tool call
                        result = await self._execute_tool_from_params(
                            session, user_id, email, tool_call["tool"], tool_call["params"]
                        )

                        # Replace the JSON in the response with a confirmation
                        processed_response = processed_response[:start_pos] + processed_response[end_pos:]
                        processed_response = processed_response.strip()
                        tools_executed = True

                        # Add a confirmation message to the user
                        if tool_call["tool"] == "add_task" and "title" in tool_call["params"]:
                            processed_response += f"\n\nI've added '{tool_call['params']['title']}' to your tasks."
                        elif tool_call["tool"] == "delete_task":
                            processed_response += f"\n\nI've deleted the task as requested."
                        elif tool_call["tool"] == "complete_task":
                            processed_response += f"\n\nI've marked the task as completed."
                        elif tool_call["tool"] == "list_tasks":
                            processed_response += f"\n\nHere are your tasks: {result}"

                except json.JSONDecodeError:
                    # Not valid JSON, continue to next match
                    continue

        return processed_response if processed_response.strip() else "Action completed successfully."

    def _extract_json_object(self, text: str, start_pos: int) -> tuple:
        """Extract a complete JSON object starting from start_pos."""
        brace_count = 0
        start_brace_pos = -1

        i = start_pos
        while i < len(text):
            char = text[i]

            if char == '{':
                if brace_count == 0:
                    start_brace_pos = i  # Mark the outermost opening brace
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_brace_pos != -1:
                    # We've found the matching closing brace
                    json_str = text[start_brace_pos:i+1]
                    return json_str, i+1  # Return the JSON string and the position after it

            i += 1

        # If we get here, we couldn't find a complete JSON object
        return None, start_pos

    async def _execute_tool_from_params(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
        tool_name: str,
        params: dict
    ) -> Any:
        """Execute a tool call based on the tool name and parameters."""
        if tool_name == "add_task":
            title = params.get("title", "")
            description = params.get("description", "")
            return await TaskTools.add_task(
                session=session,
                user_id=user_id,
                title=title,
                description=description
            )

        elif tool_name == "list_tasks":
            status = params.get("status")
            limit = params.get("limit")
            return await TaskTools.list_tasks(
                session=session,
                user_id=user_id,
                status=status,
                limit=limit
            )

        elif tool_name == "complete_task":
            task_id = str(params.get("task_id", ""))
            return await TaskTools.complete_task(
                session=session,
                user_id=user_id,
                task_id=task_id
            )

        elif tool_name == "delete_task":
            task_id = str(params.get("task_id", ""))
            return await TaskTools.delete_task(
                session=session,
                user_id=user_id,
                task_id=task_id
            )

        elif tool_name == "update_task":
            task_id = str(params.get("task_id", ""))
            title = params.get("title")
            description = params.get("description")
            completed = params.get("completed")
            return await TaskTools.update_task(
                session=session,
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                completed=completed
            )

        elif tool_name == "get_current_user":
            return await IdentityTool.get_current_user(user_id, email)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    # -----------------------------
    # Main entry point
    # -----------------------------

    async def process_message(
        self,
        session: AsyncSession,
        user_id: str,
        email: str,
        message_content: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:

        try:
            conversation_id = await self._create_or_get_conversation(
                session, conversation_id, user_id
            )

            await self._save_message(
                session, conversation_id, user_id, "user", message_content
            )

            history = await self._get_conversation_history(
                session, conversation_id
            )

            # First, try the intent detection approach
            intent = self._detect_intent(message_content)

            if intent:
                # Extract the actual task information from the message
                extracted_info = self._extract_task_info(message_content, intent)

                tool_result = await self._execute_tool(
                    session=session,
                    user_id=user_id,
                    email=email,
                    tool=intent,
                    message=extracted_info
                )

                explain_prompt = f"""
                An action was performed successfully.

                Action: {intent}
                Result: {tool_result}

                Respond to the user in one short, friendly sentence.
                """

                response = await self.cohere_client.chat(
                    message=explain_prompt,
                    temperature=0.3
                )

                assistant_response = response.text
            else:
                # Use the Cohere AI to generate a response
                response = await self.cohere_client.chat(
                    message=message_content,
                    chat_history=history,
                    temperature=0.5
                )

                # Get the raw response text from AI
                assistant_response = response.text

                # Check if the response contains JSON tool calls and execute them
                # This processes the AI response to extract and execute any JSON tool calls
                assistant_response = await self._process_ai_response_for_tools(
                    session, user_id, email, assistant_response, history
                )

            await self._save_message(
                session, conversation_id, user_id, "assistant", assistant_response
            )

            return {
                "conversation_id": conversation_id,
                "message": assistant_response,
                "tool_result": None,  # Updated to reflect that tool results are embedded in the response
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logging.error(str(e))
            return {
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "message": "Sorry, something went wrong while processing your request.",
                "tool_result": None,
                "timestamp": datetime.utcnow().isoformat()
            }
