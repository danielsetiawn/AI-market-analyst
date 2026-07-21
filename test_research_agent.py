from agents.research_agent import ResearchAgent

agent = ResearchAgent()

result = agent.run(
    ticker="BBCA.JK",
    raw_context=(
        "Bank BCA melaporkan kenaikan laba bersih kuartalan sebesar 8% YoY. "
        "Beberapa analis menyoroti potensi perlambatan pertumbuhan kredit "
        "di sektor konsumer pada kuartal berikutnya."
    ),
)

print("Ticker:", result["ticker"])
print("Summary:", result["summary"])
print("Sentiment score:", result["sentiment_score"])
print("Key findings:", result["key_findings"])