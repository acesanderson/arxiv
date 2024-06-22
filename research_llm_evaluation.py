from query_papers import query_papers
from Chain import Chain, Prompt, Model, Response
import re
from jinja2 import Template

queries = """
1. Quality Metrics:

- Evaluating coherence and factual accuracy in AI-generated text
- Metrics for assessing relevance and grammatical correctness of LLM outputs
- Automated measurement of style consistency in language model generations

2. Cross-Domain Evaluation:

- Assessing LLM performance across multiple domains and tasks
- Evaluating AI-generated content in diverse fields like creative writing and technical documentation
- Cross-domain generalization of language model evaluation techniques

3. Scalability:

- Efficient methods for evaluating large volumes of AI-generated text
- Scalable approaches to assessing entire datasets of LLM outputs
- High-throughput evaluation techniques for massive language model generations

4. Consistency:

- Measuring consistency of LLM-based evaluations across multiple runs
- Assessing reliability of AI evaluations using different models
- Techniques for ensuring stable and reproducible AI-based assessments

5. Correlation with Human Judgment:

- Comparing AI-based evaluations with expert human assessments
- Methods for aligning automated text evaluation with human judgments
- Bridging the gap between machine and human evaluation of AI-generated content

6. Multi-Model Consensus:

- Ensemble approaches for evaluating AI-generated text
- Combining multiple LLMs for more robust content assessment
- Consensus-based evaluation systems using diverse language models

7. Fine-tuning for Evaluation:

- Specialized fine-tuning techniques for AI evaluation tasks
- Improving LLM performance in assessing other AI-generated content
- Transfer learning approaches for enhancing AI evaluation capabilities

8. Prompt Engineering for Evaluation:

- Optimizing prompts for better AI-based text evaluation
- Techniques for designing effective evaluation prompts for language models
- Impact of prompt engineering on the quality of AI-generated assessments
""".strip()

# split queries into the numbered sections
sections = re.split('^[0-9]+. ', queries, flags=re.MULTILINE)[1:]

all_queries = []
for section in sections:
    title = re.findall('^(.+):', section)[0]
    queries = re.findall('- (.+)', section)
    query_dicts = []
    for query in queries:
        queries_dict = {'query': query, 'papers': query_papers(query)}
        query_dicts.append(queries_dict)
    all_queries.append({'title': title, 'queries': query_dicts})

# get all of the paper titles for an individual query
all_queries[0]['queries'][0]['papers']['ids']

# get all of the paper titles, total
results = ""
for section in all_queries:
    results += section['title'] + '\n'
    for query in section['queries']:
        results += '\t' + query['query'] + '\n'
        for paper in section['queries'][0]['papers']['ids'][0]:
            # our ids unfortunately have newlines and doubled spaces within them, luckily we can use the arxiv id if we need.
            paper = paper.replace('\n','')
            paper = paper.replace('  ', ' ')
            results += '\t\t' + paper + '\n'

with open('results.txt', 'w') as f:
    f.write(results)

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

prompt_variables['research_query'] = """
I want a survey of prompting techniques for LLM development, with specific examples from Arxiv.org papers, and a
focus on what makes an effective LLM prompt.
""".strip()

prompt_variables['use_case'] = """
I want to develop a cookbook of prompt templates from Arxiv.org research.
This cookbook will be composed of a list of prompts, each of them with a title, a paragraph desrcibing their use
case, the actual prompt text, and the arxiv id of the paper that they're from.
I will be using this cookbook of prompts in AI engineering, and they will provide a corpus from which I can experiment
with automated prompt generation.
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

Return your answer as a list of dicts, where each dict has a key 'topic' and a key 'queries', with queries being a list of query strings.
""".strip())

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
response = instructor_query(research_prompt, response_model=Topics, system_message=persona_system_message)

# print out topics into a string so we can pass to next LLM call
topics = ""
for topic in response.topics:
    topics += topic.topic + '\n'
    topics += topic.description + '\n\n'
topics = topics.strip()

prompt_variables['topics'] = topics

# render our second prompt
vector_db_prompt = prompts['vector_database_queries_prompt'].render(prompt_variables)

# second LLM call
response = instructor_query(vector_db_prompt, response_model=TopicQueriesList, system_message=persona_system_message)
topicquerieslist = response.topics

# flatten the list of topics and queries
queries = []
for topic in topicquerieslist:
    for query in topic.queries:
        queries.append({'topic': topic.topic, 'query': query})

# search the papers
for query in queries:
    query['papers'] = query_papers(query['query'])

# flatten the papers
papers = []
for query in queries:
    for paper in query['papers']['ids'][0]:
        paper = paper.replace('\n','')
        paper = paper.replace('  ', ' ')
        papers.append({'topic': query['topic'], 'query': query['query'], 'paper': paper})

