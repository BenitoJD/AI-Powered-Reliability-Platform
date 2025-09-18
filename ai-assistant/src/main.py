import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import List, TypedDict

# --- Environment Setup ---
# Make sure to set your OPENAI_API_KEY environment variable
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# --- Qdrant Vector Store Setup ---
# In a real application, this would be a persistent, remote Qdrant instance.
# For this example, we'll use an in-memory version.
embeddings = OpenAIEmbeddings()
vectorstore = Qdrant.from_texts(
    ["The web server is returning a 503 error.", "Database connection is timing out.", "The frontend is not loading correctly."],
    embedding=embeddings,
    location=":memory:",  # Use in-memory storage
    collection_name="troubleshooting_docs",
)
retriever = vectorstore.as_retriever()

# --- LLM and Prompt Setup ---
prompt = ChatPromptTemplate.from_template("""You are an expert troubleshooting assistant. Answer the user's question based on the following context:

{context}

Question: {question}
""")
llm = ChatOpenAI(temperature=0)
chain = prompt | llm | StrOutputParser()

# --- LangGraph State Definition ---
class GraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str

# --- LangGraph Nodes ---
def retrieve_documents(state):
    """
    Retrieves documents from the vector store.
    """
    print("---RETRIEVING DOCUMENTS---")
    question = state["question"]
    documents = retriever.get_relevant_documents(question)
    print(f"Retrieved: {[doc.page_content for doc in documents]}")
    return {"documents": [doc.page_content for doc in documents], "question": question}

def generate_answer(state):
    """
    Generates an answer using the retrieved documents.
    """
    print("---GENERATING ANSWER---")
    question = state["question"]
    documents = state["documents"]
    generation = chain.invoke({"context": documents, "question": question})
    print(f"Generated: {generation}")
    return {"documents": documents, "question": question, "generation": generation}

def decide_relevance(state):
    """
    Determines if the retrieved documents are relevant.
    In a real app, this would be a more complex check, maybe another LLM call.
    """
    print("---CHECKING DOCUMENT RELEVANCE---")
    documents = state["documents"]
    if not documents:
        print("No documents found. Ending.")
        return "end"
    print("Documents are relevant. Generating answer.")
    return "generate"

# --- Build the Graph ---
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)

# Build the graph
workflow.set_entry_point("retrieve")
workflow.add_conditional_edges(
    "retrieve",
    decide_relevance,
    {
        "generate": "generate",
        "end": END,
    },
)
workflow.add_edge("generate", END)

# Compile the graph
app = workflow.compile()

def main():
    """
    Main function to run the AI assistant.
    """
    print("AI assistant ready. Type 'exit' to quit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        
        # Stream the graph execution
        for output in app.stream({"question": user_input}):
            for key, value in output.items():
                print(f"Finished node '{key}':")
        
        # The final generation is in the 'generate' node's output
        final_generation = list(app.stream({"question": user_input}))[-1].get('generate', {}).get('generation')
        if final_generation:
            print("\n---FINAL RESPONSE---")
            print(final_generation)
        else:
            print("\n---NO RESPONSE GENERATED---")
        print("\n" + "="*30 + "\n")

if __name__ == "__main__":
    main()

