from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.tools.render import format_tool_to_openai_function
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a marketing manager at a manufacturer of sugar free lollies. You have been tasked with identifying the top 3 market drivers of sugar free lollies. Use the OpenAI API to search the web for the top 3 market drivers of sugar free lollies and display the results in JSON format.",
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


from langchain.schema.messages import AIMessage, HumanMessage

chat_history = []


load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

from langchain.agents import load_tools
tools = load_tools(["google-serper"], llm=llm)

import tools as tools_
tools = tools + tools_.tools

llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)

from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

question = """
- Search the web for the top 3 market drivers of electric cars using the OpenAI API.
- save the market drivers data to be used later as dict in the global variable market_drivers (
    - market_drivers: json
    for example market drivers for ev cars: 
    {
        "environmental concerns": "The increasing environmental concerns are driving the demand for electric cars.",
        "government incentives": "The availability of government incentives is driving the demand for electric cars.",
        "technological advancements": "The rapid technological advancements in electric car technology are driving the demand for electric cars."
    }
    save in same format for current market drivers
)
"""
result = agent_executor({"input": question, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=question),
        AIMessage(content=result["output"]),
    ]
)
print(result["output"])
print(tools_.market_drivers)

selected = None
while not selected == "exit":
    print(tools_.market_drivers)
    selected = None
    # select one from the market drivers
    while True:
        try:
            value = input('Select one of the market drivers: ')
            if value == "exit":
                break
            selected = tools_.market_drivers[value]
            break
        except:
            continue

    print(selected)

    question = f"""
    saved_market_drivers = {tools_.market_drivers}
    market driver selected: {selected}

    If a market driver is selected:
        - Search the web again using the OpenAI API to find statistical evidence to support it.
        - Display the statistical evidence.
        - Show evidence in deatiled format with sources.
        - Show everything in JSON format.
    """
    result = agent_executor({"input": question, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=question),
            AIMessage(content=result["output"]),
        ]
    )
    print(result["output"])