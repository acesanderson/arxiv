from query_papers import query_db
from Chain import Chain, Prompt, Model, Response
import re

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
        queries_dict = {'query': query, 'papers': query_db(query)}
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

# Define our prompt variabls

persona = """
You're an academic librarian with access to the entire catalogue of AI research papers on Arxiv.org.
You have an advanced phd in machine learning, and you have a deep understanding of traditional practices in machine
learning and natural language procesing, particularly LLMs.
Despite your deep technical knowledge, you are not a researcher yourself, and you are not familiar with the latest
research trends in the field.
You have a special talent for understanding complex technical concepts and explaining them in simple termss,
particular in reference to a very concrete business use case.
""".strip()

research_query = """
I want a survey of prompting techniques for LLM development, with specific examples from Arxiv.org papers, and a
focus on what makes an effective LLM prompt.
""".strip()

use_case = """
I want to develop a cookbook of prompt templates from Arxiv.org research.
This cookbook will be composed of a list of prompts, each of them with a title, a paragraph desrcibing their use
case, the actual prompt text, and the arxiv id of the paper that they're from.
I will be using this cookbook of prompts in AI engineering, and they will provide a corpus from which I can experiment
with automated prompt generation.
""".strip()

# Define our prompt templates

persona_system_message = """
{{persona}}
""".strip()

initial_research_prompt = """
I am interested in the following topic:
==============
{{topic}}
==============

For this purpose:
==============
{{use_case}}
==============

From your understanding of the existing academic literature on this topic, please provide a
detailed description of the research questions, methods, and findings that are most relevant to this topic.
""".strip()

vector_database_queries_prompt = """
I have a dataset of all the AI papers from arxiv.org.
I have all of the abstracts in a vector database, and I will be using similarity search
to identify papers that address the above considerations. For 1-8 above, please give me a
set of search queries (each of sentence length) that will help me find the abstracts most
likely to coverage each of the points. Provide at least 3 for each of the research items above.

Return your answer as a list of dicts, where each dict has a key 'topic' and a key 'queries', with queries being a list of query strings.
""".strip()


