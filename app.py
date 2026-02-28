from flask import Flask, request, jsonify, render_template
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from weaviate_service import WeaviateService
from cargar import load_documents

app = Flask(__name__)

llm = Ollama(model="llama3.2")
weaviate_service = WeaviateService()

prompt = PromptTemplate.from_template(
"""
You are a literary assistant.

IMPORTANT:
You must answer STRICTLY using only the information contained in the provided context.
You are NOT allowed to use prior knowledge.
If the answer is not explicitly or clearly supported by the context,
you MUST respond EXACTLY with:

"I could not find this information in the loaded books."

Context:
{context}

Question:
{question}

Answer:
"""
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/load", methods=["POST"])
def load():
    result = load_documents(weaviate_service)
    return jsonify(result)

@app.route("/books", methods=["GET"])
def books():
    res = weaviate_service.collection.query.fetch_objects(limit=1000)
    sources = {obj.properties["source"] for obj in res.objects}
    return jsonify({"books": list(sources)})

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")
    
    chunks = weaviate_service.search(question)
    if not chunks:
        return jsonify({
            "answer": "I could not find this information in the loaded books."
        })

    context = "\n".join(chunks)
    response = llm.invoke(prompt.format(context=context, question=question))
    return jsonify({"answer": response})

if __name__ == "__main__":
    app.run(port=8090, debug=True)