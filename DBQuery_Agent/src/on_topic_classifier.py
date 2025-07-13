from langchain_core.messages import BaseMessage,AIMessage,HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from pydantic import BaseModel, Field
from state import AgentState
from utils import *
from dotenv import load_dotenv
from agentops.sdk.decorators import agent, operation
load_dotenv()

schema_knowledge = describe_schema(db_path)

class ClassifyQuestion(BaseModel):
    on_topic_label:str = Field(description = 'Is the question based on the schema described and can be\
                                            converted into a SQL Query?If yes -> "Yes" if not -> "No"')

@agent(name="Topic_Classifier_Agent")
class TopicClassifier:

    # def __init__(self,state: AgentState):
    #     self.state = state

    @staticmethod
    @operation(name="query_classification_function")
    def on_topic_classifier(state:AgentState):
        #print("Inside On Topic Classifier, at present the state is:",state)

        print("\nQuery Classification Started")
        recent_question = state['question'].content
        sys_message = SystemMessage(content= """ You are classifier that determine's if the user's question is about the following database:
                The Chinook database is a sample SQL database that simulates a digital music store. \
                It contains tables for artists, albums, tracks, customers, invoices, and employees.
                The following is the schema description of the database:
                {schema_database}
                Use the database description and schema description to understand,\
                if the question is relevant and is in the bounds of the above database, respond with a 'Yes'.Otherwise respond with a 'No'
                                        """.format(schema_database=schema_knowledge))

        #print(list(state.keys()))
        if len(list(state.keys())) <= 1:
            state['messages'] = []
            state['question_history'] = []
            #state['reflection_iterations'] = 0

        ## add question history and messages ##
        state['question_history'].append(state['question'])
        state['messages'].append(state['question'])

        human_message = HumanMessage(content=f"User Question: {state['question'].content}")
        classfier_prompt_template = ChatPromptTemplate.from_messages([sys_message,human_message])
        structure_llm = llm_model.with_structured_output(ClassifyQuestion)
        classifier_chain = classfier_prompt_template | structure_llm
        on_topic_res = classifier_chain.invoke({})
        ### add the AI message and on topic classifier ###
        state['messages'].append(AIMessage(content=on_topic_res.on_topic_label.strip(),additional_kwargs={'pydantic_model':on_topic_res.__class__.__name__}))
        state['on_topic_classifier'] = str(on_topic_res.on_topic_label.strip())
        state['reflection_iterations'] = 0
        state['full_reflection_iter'] = 0
        #print("state after topic classifier:",state)

        print("Query Classification Done")
        return state

if __name__ == "__main__":
    #classifier = TopicClassifier()
    state1 = TopicClassifier.on_topic_classifier({'question':HumanMessage(content="List all customers in alphabetical order")})
    print('state after classifier:',state1)