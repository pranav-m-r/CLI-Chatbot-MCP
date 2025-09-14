from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name="read_doc_contents",
    description="Reads the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="The ID of the document to read."),
) -> str:
    if doc_id not in docs:
        return ValueError(f"Document with ID {doc_id} not found.")
    
    return docs[doc_id]

@mcp.tool(
    name="edit_doc_contents",
    description="Edits a document by replacing a string in the document contents with a new string.",
)
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit."),
    old_string: str = Field(description="The string to be replaced in the document."),
    new_string: str = Field(description="The string to replace the old string with."),
):
    if doc_id not in docs:
        return ValueError(f"Document with ID {doc_id} not found.")
    
    if old_string not in docs[doc_id]:
        return ValueError(f"String '{old_string}' not found in document {doc_id}.")
    
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_documents() -> list[str]:
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def get_document(doc_id: str) -> str:
    if doc_id not in docs:
        return ValueError(f"Document with ID {doc_id} not found.")
    
    return docs[doc_id]

@mcp.prompt(
    name="format",
    description="Rewrites the contents of a document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="The ID of the document to format.")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document into Markdown format.

    The id of the document to format is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, and other Markdown formatting as appropriate.
    Use the 'edit_document' tool to edit the document.
    After the document is formatted, use the 'read_document' tool to read the contents of the document and return it.
    """

    return [base.UserMessage(prompt)]

# TODO: Write a prompt to summarize a doc
@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of a document."
)
def summarize_document(
    doc_id: str = Field(description="The ID of the document to summarize.")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize a document.

    The id of the document to summarize is:
    <document_id>
    {doc_id}
    </document_id>

    Provide a concise summary of the document's key points.
    Use the 'read_document' tool to read the contents of the document.
    """

    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
