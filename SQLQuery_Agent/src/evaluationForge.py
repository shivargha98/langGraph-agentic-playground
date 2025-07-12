import phoenix as px
import json
import pandas as pd
from phoenix.experiments import evaluate_experiment, run_experiment
from phoenix.experiments.evaluators import create_evaluator
# from phoenix.trace import ann
import opentelemetry
from openinference.semconv.trace import SpanAttributes
import uuid
from sql_generator import *
from utils import *
from phoenix.experiments.types import Example


id = str(uuid.uuid4())
######################
px_client = px.Client() ##client to upload to pheonix UI##
### ground truth data as List of dicts ####
with open('.\src\ground_truth_dataset.json', 'r') as file:
    data = json.load(file)
print(data)
#####################

####### creating the dataframe ######
query_df = pd.DataFrame.from_dict(data=data)
#############################
#print(query_df.head())

dataset = px_client.upload_dataset(
    dataframe=query_df[0:2],
    dataset_name=f"Sqlquery_ground_truth_{id}",
    input_keys=["input"],
    output_keys=["expected_sql"],
)

def sql_generation_step(example:Example) -> str:

    sql_response = SQLGen_agent.sqlgen_for_eval(example.input.get("input"))
    print('SQL Generated:',sql_response)
    #current_span = opentelemetry.trace.get_current_span()
    #current_span.set_attribute(SpanAttributes.INPUT_VALUE, example.input.get("input"))
    #current_span.set_attribute(SpanAttributes.OUTPUT_VALUE, sql_response)
    return {"output":sql_response}

# custom_sql_evaluator = create_evaluator(
#     name="execution_accuracy_eval",
#     #task="custom",
#     prediction_function=structural_similarity
# )


experiment = run_experiment(
    dataset,
    sql_generation_step,
    evaluators=[structural_similarity],
    
    experiment_name="SQL Query evaluation",
    experiment_description="SQL Query evaluation, comparing ground truths and predicted queries",
)

# print(experiment.runs[0].inputs,experiment.runs[0].outputs)
# for run_id, run in experiment.runs.items():
#     print(f"Run ID: {run_id}")
#     print("Input:", run)
#     print("Output:", run)
#     print("-" * 40)

print("\n ------ Done Experimentation -------")