from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage
from state import *
from tools import *
from utils import *
import json
from agentops.sdk.decorators import agent,operation

@agent(name="ReACT_agent")
class ReACT:
    @staticmethod
    @operation(name="Act_operation")
    def act(state:AgentState):

        print("\nThinking of an Action based on the user Query and data extracted from database")
        tools = [text_listing_tool, bar_chart_tool, line_chart_tool]
        llm_with_tools = llm_model.bind_tools(tools)
        
        ACT_PROMPT = '''
        You are a data visualization agent. Based on the following context, choose the appropriate tool from one of the following:
        - `bar_chart_tool`: use when one column is categorical (like names, genres) and another is numeric.
        - `line_chart_tool`: use when one column is a time/date and another is numeric (e.g., monthly revenue).
        - `text_listing_tool`: use when data is purely text-based.
        
        Respond by calling the correct tool with the appropriate SQL result data.
        
        ---
        
        User Query: {user_query}
        
        LLM's SQL Response: {ai_message}
        
        SQL Query Result (sample): {sql_result}
        
        Column Names: {column_names}
        '''
        
        prompt_template = ChatPromptTemplate.from_template(ACT_PROMPT)
        chain = prompt_template | llm_with_tools
        ai_message = chain.invoke({'user_query':state['messages'][-2].content,
                    'ai_message':state['messages'][-1].content,
                    'sql_result':state['sql_result'][-1],
                    'column_names':state['sql_query_columns']})
        state['messages'].append(ai_message)

        #print("\n State after Act Node:",state)

        print("Completed Thought, Taking action")
        return state
    
    @staticmethod
    @operation(name="execute_tool_operation")
    def execute_tools(state:AgentState):

        tools = [text_listing_tool, bar_chart_tool, line_chart_tool]
        tools_by_name = {tool.name: tool for tool in tools}

        ##check for ai message##
        if isinstance(state['messages'][-1],AIMessage):
            ai_message = state['messages'][-1]
            if hasattr(ai_message,"tool_calls"):
                #tool_messages = []
                
                for tool_call in ai_message.tool_calls:
                    print("\nUsing {} for visualisation".format(tool_call['name']))
                    tool_call_function = tool_call['name']
                    call_id = tool_call["id"]
                    if tool_call_function == 'text_listing_tool':
                        data = json.loads(state['sql_result'])
                        title = state['question'].content
                        path = tools_by_name[tool_call['name']].invoke({'data':data,'title':title})
                        state['messages'].append(
                            ToolMessage(
                                content = "Plot saved at: "+path,
                                tool_call_id = call_id,
                                tool_name = tool_call['name'] ##required for gemini
                            )
                        )
                        state['next_tool_selection'] = tool_call['name']

                    else:
                        data = json.loads(state['sql_result'])
                        title = state['question'].content
                        x_axis = state['sql_query_columns'][0]
                        y_axis = state['sql_query_columns'][1]
                        path = tools_by_name[tool_call['name']].invoke({'data':data,'title':title,\
                                        'x_axis':x_axis,'y_axis':y_axis})
                        state['messages'].append(
                            ToolMessage(
                                content = "Plot saved at: "+path,
                                tool_call_id = call_id,
                                tool_name = tool_call['name'] ##required for gemini
                            )
                        )
                        state['next_tool_selection'] = tool_call['name']
                #print("\n State after tool execution:",state)
                print("Executed the tool")
                return state
            else:
                print("No tool was required")
                return state