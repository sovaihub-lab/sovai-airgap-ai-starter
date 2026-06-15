from app.agent import LocalAgentRuntime
from app.rag import PrivateRAG
from app.ml import TinyMLClassifier

def test_blocks_unapproved_tool():
    agent = LocalAgentRuntime(PrivateRAG(), TinyMLClassifier())
    result = agent.run("web_search", "latest AI news")
    assert result["allowed"] is False
