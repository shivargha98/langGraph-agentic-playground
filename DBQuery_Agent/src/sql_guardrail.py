from state import AgentState
from guardrails import Guard
from guardrails.hub import ExcludeSqlPredicates
from sqlglot import expressions as exp
from agentops.sdk.decorators import agent, operation


guard = Guard().use(
    ExcludeSqlPredicates, predicates = ['Drop','Delete'], on_fail = "reask"
    )
# response = guard.validate("SELECT * FROM GHC")
# print(response)


@operation
def SQL_guard(state:AgentState):

    #print("inside guardrail:",state)
    print("\nGuardrails activated")
    if "guardrail_validation" not in state or state["guardrail_validation"] is None:
        state["guardrail_validation"] = []

    sql_query = state['sql_query']

    try:
        response = guard.validate(sql_query)
        state['guardrail_validation'].append("validation_success")
        #print("state after guardrail:",state)
        print("Guardrail validation passed")
    except:
        state['guardrail_validation'].append("validation_failed")
        #print("\nstate after guardrail:",state)
        print("Guardrail validation failed")

    return state



