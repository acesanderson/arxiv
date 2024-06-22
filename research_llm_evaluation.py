from query_papers import query_papers
from Chain import Chain, Prompt, Model, Response
import re

# Define our prompt variables
prompt_variables = {}

prompt_variables['persona'] = """
You're an academic librarian with access to the entire catalogue of AI research papers on Arxiv.org.
You have an advanced phd in machine learning, and you have a deep understanding of traditional practices in machine
learning and natural language procesing, particularly LLMs.
Despite your deep technical knowledge, you are not a researcher yourself, and you are not familiar with the latest
research trends in the field.
You have a special talent for understanding complex technical concepts and explaining them in simple termss,
particularly in reference to a very concrete business use case.
""".strip()

# prompt_variables['research_query'] = """
# I want a survey of prompting techniques for LLM development, with specific examples from Arxiv.org papers, and a
# focus on what makes an effective LLM prompt.
# """.strip()

# prompt_variables['use_case'] = """
# I want to develop a cookbook of prompt templates from Arxiv.org research.
# This cookbook will be composed of a list of prompts, each of them with a title, a paragraph desrcibing their use
# case, the actual prompt text, and the arxiv id of the paper that they're from.
# I will be using this cookbook of prompts in AI engineering, and they will provide a corpus from which I can experiment
# with automated prompt generation.
# """.strip()

prompt_variables['research_query'] = """
How do you evaluate the quality of LLM output using LLMs? I am NOT interesting in evaluating LLM models, but rather
the prompt engineering and flow orchestration that be utilized to evaluate the quality of generated content.
""".strip()

prompt_variables['use_case'] = """
I will be using LLMs to publish content, like text courses and assesments and other text-based content.
My main challenge is to generate high-quality content that is both engaging and informative, and I want to
create prompt flows and experiment with prompt engineering as well as employ other LLM development techniques in order
to optimize the final product. #1 on my agenda is identifying ways to score the quality of the LLM-generated content with LLMs.
""".strip()

# Define our prompt templates
prompts = {}

prompts['persona_system_message'] = Prompt("""
{{persona}}
""".strip())

prompts['initial_research_prompt'] = Prompt("""
I have the following research query:
==============
{{research_query}}
==============

For this purpose:
==============
{{use_case}}
==============

From your understanding of the existing academic literature related to this query, please provide a
detailed description of 5-8 research questions, methods, and findings that are most relevant to this topic.
Aim for specificity -- i.e. not "natural language processing" but "the use of transformers in NLP tasks".
For each topic, provide:
(1) topic title
(2) a paragraph description of the topic at least 200 characters long.
""".strip())

prompts['vector_database_queries_prompt'] = Prompt("""
I have a dataset of all the AI papers from arxiv.org.
I have all of the abstracts in a vector database, and I will be using similarity search
to identify papers that address the above considerations.

Here are some research topics:
==============
{{topics}}
==============

For each of the above topics, please give me a set of search queries (each of sentence
length) that will help me find the abstracts most likely to coverage each of the points. 
Provide at least 3 for each of the research items above.
""".strip())

# Return your answer as a list of dicts, where each dict has a key 'topic' and a key 'queries', with queries being a list of query strings.

# =============================================================================
# this is implementation with Chain Framework; we will also implement with Instructor as comparison.
## Set up chains; we will refactor this with Instructor at a later day.
## new create_messages function works great!
# messages = Chain.create_messages(prompts['persona_system_message'], prompt_variables)

# def initial_research(prompt_variables: dict = prompt_variables, prompts: dict = prompts, messages = messages) -> Response:
#     """
#     Conducts initial research based on the provided prompt variables.
#     Likely need to add more clarity, some examples of output, and json prompting + parsing.
#     """
#     prompt = prompts['initial_research_prompt']
#     model = Model('claude')
#     chain = Chain(prompt, model)
#     response = chain.run(input = prompt_variables, messages = messages)
#     return response

# def compose_vector_database_queries(prompt_variables: dict = prompt_variables, prompts: dict = prompts, messages = messages) -> Response:
#     """
#     For each topic identified from previous research, composes a set of search queries for the vector database.
#     """
#     prompt = prompts['vector_database_queries_prompt']
#     model = Model('claude')
#     chain = Chain(prompt, model)
#     response = chain.run(input = prompt_variables, messages = messages)
#     return response

# response = initial_research()
# messages = response.messages

# # add topics to prompt variables
# prompt_variables['topics'] = response.content

# # get the response from the vector database queries
# response = compose_vector_database_queries(prompt_variables, prompts, messages)

# =============================================================================
import instructor
from pydantic import BaseModel, constr          # constr is a string type with constraints, max_length and min_length
from anthropic import Anthropic
from Chain import Chain

# Add the OpenAI API key to the environment (locals())
anthropic_api_key = Chain.api_keys['ANTHROPIC_API_KEY']

client = instructor.from_anthropic(Anthropic())

# Define your desired output structure as Pydantic classes
class Topic(BaseModel):
    topic: str
    description: constr(min_length=200)

class Topics(BaseModel):
    topics: list[Topic]

class TopicQueries(BaseModel):
    topic: str
    queries: list[str]

class TopicQueriesList(BaseModel):
    topics: list[TopicQueries]

# Our query function
def instructor_query(query, model='claude-3-5-sonnet-20240620', max_tokens=1024, response_model = None, system_message = ""):
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        system = system_message,
        response_model=response_model,
    )
    return response

# render our prompts
persona_system_message = prompts['persona_system_message'].render(prompt_variables)
research_prompt = prompts['initial_research_prompt'].render(prompt_variables)

# first LLM call
research_response = instructor_query(research_prompt, response_model=Topics, system_message=persona_system_message)

# print out topics into a string so we can pass to next LLM call
topics = ""
for topic in research_response.topics:
    topics += topic.topic + '\n'
    topics += topic.description + '\n\n'

topics = topics.strip()

prompt_variables['topics'] = topics

# render our second prompt
vector_db_prompt = prompts['vector_database_queries_prompt'].render(prompt_variables)

# second LLM call
queries_response = instructor_query(vector_db_prompt, response_model=TopicQueriesList, system_message=persona_system_message)
topicquerieslist = queries_response.topics

# flatten the list of topics and queries
final_queries = []
for q in topicquerieslist:
    for final_query in q.queries:
        final_queries.append({'topic': topic.topic, 'query':final_query})

# search the papers
for q in final_queries:
    q['papers'] = query_papers(q['query'])

# flatten the papers
papers = []

for query in final_queries:
    for paper in query['papers']['ids'][0]:
        paper = paper.replace('\n','')
        paper = paper.replace('  ', ' ')
        papers.append({'topic': query['topic'], 'query': query['query'], 'paper': paper})

# We now have the papers. Need to be able to implement retries.