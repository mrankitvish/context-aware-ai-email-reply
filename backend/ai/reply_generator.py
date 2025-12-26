from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
from backend.core.security import check_safety
import json

class ReplyState(TypedDict):
    summary: dict
    tone: str
    instructions: Optional[str]
    reply: Optional[str]
    quality_check_passed: bool
    retries: int
    error: Optional[str]

class ReplyGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(ReplyState)

        workflow.add_node("generate_reply", self.generate_reply)
        workflow.add_node("validate_reply", self.validate_reply)

        workflow.set_entry_point("generate_reply")

        workflow.add_edge("generate_reply", "validate_reply")
        
        workflow.add_conditional_edges(
            "validate_reply",
            self.check_quality,
            {
                "stop": END,
                "retry": "generate_reply"
            }
        )

        return workflow.compile()

    def generate_reply(self, state: ReplyState):
        summary = state["summary"]
        tone = state["tone"]
        instructions = state.get("instructions")
        retries = state.get("retries", 0)
        
        # If retrying, maybe adjust prompt? For now, just retry.
        
        prompt_text = """
        You are a professional email assistant.
        
        CONTEXT:
        - Intent: {intent}
        - Sentiment: {sentiment}
        - Urgency: {urgency}
        - Thread Summary: {thread_summary}
        
        CUSTOMER EMAIL SUMMARY:
        Main Topic: {main_topic}
        Questions: {questions}
        Action Items: {action_items}
        
        INSTRUCTIONS:
        - Write a {tone} email reply.
        - Address all questions.
        - Be specific and helpful.
        """
        
        if instructions:
            prompt_text += f"\n        - ADDITIONAL USER INSTRUCTIONS: {instructions}\n"
            
        prompt = ChatPromptTemplate.from_template(prompt_text)
        
        chain = prompt | self.llm | StrOutputParser()
        
        reply = chain.invoke({
            "intent": summary['classification']['intent'],
            "sentiment": summary['sentiment']['label'],
            "urgency": summary['urgency']['level'],
            "thread_summary": summary['thread_info']['thread_summary'],
            "main_topic": summary['content_analysis']['main_topic'],
            "questions": "\n".join(summary['content_analysis']['questions']),
            "action_items": "\n".join(summary['content_analysis']['action_items']),
            "tone": tone
        })
        
        return {"reply": reply, "retries": retries + 1}

    def validate_reply(self, state: ReplyState):
        reply = state["reply"]
        
        # 1. Length Check
        if len(reply) < 10:
             return {"quality_check_passed": False, "error": "Reply too short"}
        
        # 2. Safety/Refusal Check
        # Use shared guardrails
        is_safe, reason = check_safety(reply)
        if not is_safe:
             return {"quality_check_passed": False, "error": f"Safety violation: {reason}"}

        # Also check for LLM refusals which might not be in the keyword list
        refusal_phrases = [
            "I cannot comply", "I can't comply", "I cannot fulfill", "I'm sorry", "I am sorry",
            "I'm unable to", "I am unable to", "cannot write", "cannot generate", "inappropriate",
            "offensive", "harmful"
        ]
        
        lower_reply = reply.lower()
        for phrase in refusal_phrases:
            if phrase in lower_reply:
                if "cannot comply" in lower_reply:
                     return {"quality_check_passed": False, "error": "Safety violation: Reply refused or inappropriate content detected."}

        return {"quality_check_passed": True, "error": None}

    def check_quality(self, state: ReplyState):
        """
        Determines whether to stop the workflow or retry.
        Returns "stop" to end the workflow (success or max retries reached).
        Returns "retry" to loop back to generation.
        """
        if state["quality_check_passed"]:
            return "stop"
        
        if state["retries"] >= 3:
            return "stop" # Max retries reached, stop workflow even if failed
            
        return "retry"

    def generate(self, summary: dict, tone: str = "professional", instructions: Optional[str] = None) -> dict:
        initial_state = ReplyState(
            summary=summary,
            tone=tone,
            instructions=instructions,
            reply=None,
            quality_check_passed=False,
            retries=0,
            error=None
        )
        
        result = self.workflow.invoke(initial_state)
        
        if not result["quality_check_passed"]:
            return {
                "status": "error",
                "error": result.get("error", "Unknown validation error"),
                "reply": result["reply"]
            }
            
        return {
            "status": "success",
            "reply": result["reply"]
        }
