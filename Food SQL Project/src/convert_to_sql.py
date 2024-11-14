from src.entity import AgentState, get_database_schema, engine, CheckRelevance, ConvertToSQL
from langchain_core.runnables.config import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
load_dotenv()

from langchain_cohere import ChatCohere
llm = ChatCohere(model = "command-r-plus-08-2024",temperature=0)

def convert_nl_to_sql(state: AgentState, config: RunnableConfig):
    question = state["question"]
    current_user = state["current_user"]
    schema = get_database_schema(engine)
    print(f"Converting question to SQL for user '{current_user}': {question}")
    system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:

        {schema}

        The current user is '{current_user}'. Ensure that all query-related data is scoped to this user.

        use sql_query to provide only the SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.
        there can be multiple question in a particular user question.
        first think before writing query
        write a query for each question.
        For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.
    """.format(schema=schema, current_user=current_user)
    convert_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Question: {question}"),
        ]
    )
    structured_llm = llm.with_structured_output(ConvertToSQL)
    sql_generator = convert_prompt | structured_llm
    result = sql_generator.invoke({"question": question})
    state["sql_query"] = result.sql_query
    print(f"Generated SQL query: {state['sql_query']}")
    return state