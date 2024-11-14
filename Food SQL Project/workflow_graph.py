from src.entity import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser
from src.get_current_user import get_current_user
from src.check_revelance import check_relevance
from src.convert_to_sql import convert_nl_to_sql
from src.execute_sql import execute_sql
from src.generate_human_readable_answer import generate_human_readable_answer
from src.regenerate_query import regenerate_query
from src.generate_funny_response import generate_funny_response
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import os
load_dotenv()

def relevance_router(state: AgentState):
    if state["relevance"].lower() == "relevant":
        return "convert_to_sql"
    else:
        return "generate_funny_response"
    
def execute_sql_router(state: AgentState):
    if not state.get("sql_error", False):
        return "generate_human_readable_answer"
    else:
        return "regenerate_query"
    
def end_max_iterations(state: AgentState):
    state["query_result"] = "Please try again."
    print("Maximum attempts reached. Ending the workflow.")
    return state

def check_attempts_router(state: AgentState):
    if state["attempts"] < 3:
        return "convert_to_sql"
    else:
        return "end_max_iterations"
    
workflow = StateGraph(AgentState)

workflow.add_node("get_current_user", get_current_user)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("convert_to_sql", convert_nl_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_human_readable_answer", generate_human_readable_answer)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("end_max_iterations", end_max_iterations)

workflow.add_edge("get_current_user", "check_relevance")

workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "convert_to_sql": "convert_to_sql",
        "generate_funny_response": "generate_funny_response",
    },
)

workflow.add_edge("convert_to_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    execute_sql_router,
    {
        "generate_human_readable_answer": "generate_human_readable_answer",
        "regenerate_query": "regenerate_query",
    },
)

workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "convert_to_sql": "convert_to_sql",
        "max_iterations": "end_max_iterations",
    },
)

workflow.add_edge("generate_human_readable_answer", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)

workflow.set_entry_point("get_current_user")

app = workflow.compile()

def chat_bot(user_id: str, query):
    config = {"configurable": {"current_user_id": user_id}}
    result = app.invoke({"question": query, "attempts": 0}, config=config)
    return result['query_result']

if __name__ == "__main__":
    chat_bot(app, "3", "how much do i need to pay for my order?")