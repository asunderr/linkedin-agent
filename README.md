# LinkedIn Content Agent Pipeline

An AI-powered content pipeline that researches, drafts, and refines LinkedIn posts 
using Claude's API. Built for executives and ghostwriters who want to produce 
high-quality thought leadership at scale.

## What It Does

- **Topic Generator** — Scans the web for timely topics in your niche and suggests 
  post ideas with recommended content types
- **Research Agent** — Pulls live data, statistics, and trends using web search
- **Draft Agent** — Produces multiple post variations matched to your voice and style
- **Refine Agent** — Quality-gates every post against C-suite readability standards
- **Auto Mode** — Runs the full pipeline unattended and saves drafts to a folder
- **Scheduled Execution** — Cron job generates fresh drafts on your chosen schedule

## Quick Start

1. Clone the repo
```bash
git clone https://github.com/asunderr/linkedin-agent.git
cd linkedin-agent
```

2. Set up Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic httpx
```

3. Add your API key
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

4. Add your example posts to `examples.py`

5. Run the interactive pipeline
```bash
python3 linkedin_pipeline.py
```

6. Or run the automated version
```bash
python3 linkedin_auto.py
```

## Customization

The pipeline is designed to be personalized:

- **Voice Guide** — Edit the system prompt in `linkedin_pipeline.py` to match your 
  writing style, approved sources, and guardrails
- **Example Posts** — Add your best-performing posts to `examples.py` so the AI 
  learns your voice
- **Content Pillars** — Update the topic generator's system prompt with your themes
- **Quality Checks** — Customize the refiner's criteria for your audience

## How It Works
Topic Generator → You Pick a Topic → Research Agent → Draft 3 Variations →
You Pick One → Refine Agent → Final Post

Each agent is a specialized Claude API call with its own system prompt. 
The output of each step feeds into the next.

## Requirements

- Python 3.9+
- Anthropic API key ([get one here](https://console.anthropic.com))
- ~$0.05 per pipeline run

## Built With

- [Anthropic Claude API](https://docs.anthropic.com) — Powers all agents
- Built from scratch in Python by a non-developer learning AI agents

## License

MIT