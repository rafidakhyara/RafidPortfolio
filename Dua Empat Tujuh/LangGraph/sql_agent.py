from crewai import Agent, Task, LLM, Crew, Process

llm = LLM(model="gpt-4o-mini",
          api_key="OPENAI_API_KEY")

sql_agent = Agent(
    role='SQL Query Writer',
    goal="To write the best queries, following the given {input}. Plan before you write.",
    backstory="You're an expert SQL user.",
    llm=llm
)

plan_task = Task(
    name="Plan SQL Query",
    description="Break down the order in which you need to obtain the information to answer the user's input. Use this order to refine how the SQL query will be written.",
    expected_output="A numbered list of the information needed, sorted in the correct order.",
    agent=sql_agent,
    llm=llm
)

write_task = Task(
    name="Write SQL Query",
    description="Write an SQL Query, but don't do it before you sort out the order in which you need to obtain information.",
    expected_output="An SQL Query. Mark the beginning of the query with 'Query:' and the end of a query with '(Query End)'.",
    agent=sql_agent,
    llm=llm
)

sql_crew = Crew(
    agents=[sql_agent],
    tasks=[plan_task, write_task],
    verbose=True,
    process=Process.sequential,
    llm=llm
)
