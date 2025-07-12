from schema_description import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where
from sqlparse.tokens import Keyword, DML

from dotenv import load_dotenv
load_dotenv()

db_path = 'Chinook_Sqlite.sqlite'
schema_knowledge = describe_schema(db_path)

llm_model = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash',max_retries=2)
llm_qwen_coder = ChatOllama(model="qwen2.5-coder:3b")
llm_judge = ChatGroq(model = 'llama-3.1-8b-instant')


##### dict of tool description #########
tool_descriptors = {
    "text_listing_tool":"Displays a list of textual entries as bullet points.Use this tool when the SQL result returns only textual data (e.g., names of albums, artists, genres).",
    "bar_chart_tool":"Generates a bar chart from categorical-numeric pairs. Use this tool when the SQL result includes categories (e.g., countries, genres) with corresponding numeric values (e.g., revenue, sales count).",
    "line_chart_tool":"Creates a line chart from time series data.Use this tool when the SQL result includes time-based keys (e.g., months, dates) and numeric values (e.g., monthly sales, revenue)."
}



def extract_sql_structure(query):
    parsed = sqlparse.parse(query)[0]
    print(parsed)
    structure = {
        "tables": set(),
        "columns": set(),
        "where_clauses": set(),
        "functions": set()
    }

    from_seen = False
    select_seen = False
    for token in parsed.tokens:
        if token.ttype is DML and token.value.upper() == "SELECT":
            select_seen = True
        if token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                structure["columns"].add(identifier.get_real_name())
        elif isinstance(token, Identifier):
            name = token.get_real_name()
            parent = token.get_parent_name()
            if from_seen:
                structure["tables"].add(name)
            elif select_seen:
                structure["columns"].add(name)
        elif isinstance(token, Where):
            structure["where_clauses"].add(str(token))
        elif token.ttype is Keyword and token.value.upper() in ["MAX", "SUM", "AVG", "COUNT"]:
            structure["functions"].add(token.value.upper())

    return structure



def structural_similarity(output: str, expected: str) -> float:
    struct1 = extract_sql_structure(output.get("output"))
    struct2 = extract_sql_structure(expected.get("expected_sql"))

    def jaccard(set1, set2):
        if not set1 and not set2:
            return 1.0
        return len(set1 & set2) / len(set1 | set2)

    scores = {}
    for key in struct1:
        scores[key] = jaccard(struct1[key], struct2[key])

    # Final score is average of all component scores
    return round(sum(scores.values()) / len(scores), 3)

if __name__ == "__main__":
    #struct = extract_sql_structure("SELECT Name FROM Track INNER JOIN Album ON Track.AlbumId = Album.AlbumId WHERE Album.Title = 'Black Album';")
    #print(struct)
    #score = structural_similarity("SELECT Name FROM Track INNER JOIN Album ON Track.AlbumId = Album.AlbumId WHERE Album.Title = 'Black Album';",
    #                              "SELECT Playlist.Name, COUNT(PlaylistTrack.TrackId) as TrackCount FROM Playlist INNER JOIN PlaylistTrack ON Playlist.PlaylistId = PlaylistTrack.PlaylistId GROUP BY Playlist.Name;")
    #print(score)
    pass