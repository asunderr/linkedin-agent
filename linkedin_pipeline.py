import anthropic
import time
import httpx
from examples import EXAMPLE_POSTS

client = anthropic.Anthropic()

MODEL = "claude-sonnet-4-20250514"

def fetch_article(url):
    print(f"📄 Fetching article...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="Read this article and extract the key arguments, data points, and insights. Be thorough but concise.",
        messages=[
            {"role": "user", "content": f"Summarize the key points from this article: {url}"}
        ],
        tools=[
            {"type": "web_search_20250305", "name": "web_search"}
        ]
    )
    
    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text + "\n"
    
    return result

    
def generate_topics():
    print("💡 Generating topic ideas...")
    
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="""You are a content strategist for a senior insurance executive who is 
CEO-in-Residence at a PE fund focused on acquiring and AI-transforming insurance 
back-office service providers (MGAs, TPAs, commercial P&C back-office).

His audience is insurance C-suite execs and PE operating partners.

His content pillars are:
1. AI transforming insurance operations (not incremental, fundamental reshaping)
2. The talent and org chart evolution driven by AI
3. Enterprise transformation lessons from 15+ years in consulting
4. The "SaaSapocalypse" - AI disrupting traditional SaaS business models
5. Private equity value creation through operational transformation

Search the web for the latest news, research, and developments in these areas.
Then suggest 5 topic ideas. For each topic provide:
- The topic in one sentence
- Why it's timely (what news or trend makes this relevant RIGHT NOW)
- Recommended content type: CONTRARIAN, FRAMEWORK, PERSONAL STORY, or THOUGHT LEADERSHIP
- A suggested hook (the first line of the post)

Focus on topics that would generate engagement from insurance executives, 
not generic AI commentary.""",
        messages=[
            {"role": "user", "content": "What should I write about this week? Find the most timely and relevant topics."}
        ],
        tools=[
            {"type": "web_search_20250305", "name": "web_search"}
        ]
    )
    
    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text + "\n"
    
    return result

# ============================================================
# AGENT 1: RESEARCHER
# ============================================================
def research(topic):
    print("🔍 Researching topic...")
    
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="""You are a research analyst supporting a senior insurance and financial 
services executive who writes LinkedIn thought leadership.

Use web search to find the latest, most relevant information on the topic.

Your job is to provide:
1. Key data points and statistics relevant to the topic (with sources)
2. Recent developments or trends from the last 1-2 weeks if possible
3. A contrarian or non-obvious angle that would make a compelling LinkedIn post
4. A specific, practical example that grounds the topic in reality

Only cite: McKinsey, Harvard Business Review, MIT, WSJ, Sequoia, OpenAI, Google, 
Anthropic, and similar tier-1 sources. NEVER cite Bain, BCG, or Big 4 firms.

Keep your research brief and actionable - this will feed directly into a post draft.""",
        messages=[
            {"role": "user", "content": f"Research this topic for a LinkedIn post: {topic}"}
        ],
        tools=[
            {"type": "web_search_20250305", "name": "web_search"}
        ]
    )

    # Extract text from the response (web search returns multiple content blocks)
    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text + "\n"
    
    return result

# ============================================================
# AGENT 2: DRAFTER
# ============================================================
def draft(topic, research_output, article_summary=None):
    print("✍️  Drafting variations...")
    
    voice_guide = """You are a LinkedIn ghostwriter for a senior executive — CEO-in-Residence 
at a PE fund acquiring and transforming insurance back-office service providers using AI. 
15+ years in insurance and financial services, most recently at McKinsey.

AUDIENCE: Insurance C-suite execs and PE operating partners. Every sentence must be 
relevant in their world.

POST STRUCTURE:
1. Hook: First line earns the "see more" click — curiosity gap or pattern interrupt
2. Tension: Name a specific problem with a real number or data point
3. The How: 3-5 concrete steps or bullets showing HOW, not just WHAT. Reader walks 
   away with a playbook.
4. Reframe: One non-obvious insight — if it could appear in any generic AI post, cut it
5. CTA: Bold statement or sharp question that invites comments

FORMAT: Short paragraphs. White space. 800-1200 characters. 3 hashtags max.

NON-NEGOTIABLE RULES:
- Only cite McKinsey, HBR, MIT, WSJ, Sequoia, OpenAI, Google, Anthropic. 
  NEVER cite Bain, BCG, Deloitte, Accenture, PwC, EY, KPMG.
- Never fabricate case studies. If no real example exists, use "Imagine an MGA 
  processing 10,000 bordereaux monthly..." to signal it's illustrative.
- Stay in lane: insurance ops, MGA/broker back-office, AI transformation, PE value 
  creation. No analogies from other industries.
- No AI slop: ban "game-changer", "unlock value", "in today's rapidly evolving 
  landscape", "let that sink in", or anything that could appear in any LinkedIn post 
  about any topic.

TONE: Write like a senior partner telling a sharp friend something interesting over 
drinks. Direct, occasionally dry humor, earned confidence. Not a press release.

See the example posts provided — match that voice and energy level."""

    drafts = []
    
    angles = [
        "Write this as a contrarian take — challenge conventional wisdom in the industry.",
        "Write this as a lessons-learned story — ground it in a specific operational scenario.",
        "Write this as a data-driven argument — lead with numbers and build to an insight."
    ]
    
    for i, angle in enumerate(angles):
        print(f"  📝 Variation {i+1}/3: {angle[:50]}...")
        
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=voice_guide,
            messages=[
                {"role": "user", "content": f"""Write a LinkedIn post about: {topic}

Angle: {angle}

Use this research to inform your post:
{research_output}

{"IMPORTANT - Reference article to anchor your post around:" + chr(10) + article_summary + chr(10) + "You MUST directly engage with this article's arguments. Cite it by name. Build on it, critique it, or apply its framework to insurance. Do not ignore it." if article_summary else ""}

Here are examples of my best-performing LinkedIn posts. Match this voice, tone, 
structure, and energy level:

{chr(10).join(f'--- EXAMPLE {i+1} ---{chr(10)}{post}' for i, post in enumerate(EXAMPLE_POSTS))}"""}
            ]
        )
        
        drafts.append(message.content[0].text)
        time.sleep(60)  # Rate limit pause between variations
    
    return drafts


# ============================================================
# AGENT 3: REFINER
# ============================================================
def refine(draft_output):
    print("🔄 Refining draft...")
    
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="""You are a senior editorial advisor who has spent 20 years working with 
McKinsey Senior Partners and Fortune 500 CEOs on their executive communications.

Your job is to take a LinkedIn post draft and make it sharper. Apply these checks 
in order:

1. SOURCE CHECK: Every statistic must have a credible source named. If a stat has 
   no source, either add the real source or rewrite the sentence without the stat. 
   Never leave an orphaned number.

2. OPERATOR HONESTY CHECK: Does anything sound too clean or too easy? Real 
   transformations are messy. If there's a step-by-step framework, add one moment 
   of "here's where it gets hard" or "here's what most people get wrong." A Senior 
   Partner earns trust by naming the difficulty, not just the solution.

3. ECONOMICS CHECK: Is there at least one number a PE exec could use in a back-of-napkin 
   calculation? Think margin impact, payback period, cost per unit, or FTE savings 
   translated to dollars. "Saved 12 hours/week" should become "Saved 12 hours/week — 
   roughly $150K annually across a 20-person ops team."

4. CLOSING CHECK: Does the post end with a genuine point of view or a sharp, specific 
   question? Kill any generic engagement bait like "What do you think?" or "Which part 
   of your process..." Replace with either a bold stance or a question so specific that 
   only someone in the industry could answer it.

5. SLOP CHECK: Cut any phrase that could appear in any LinkedIn post about any topic. 
   If a sentence doesn't make an insurance CEO think "this person knows my world," 
   delete it.

6. COMPETITOR CHECK: Any reference to Bain, BCG, Deloitte, Accenture, PwC, EY, or 
   KPMG must be removed entirely.

Return ONLY the final post text, ready to publish. No commentary or notes.""",
        messages=[
            {"role": "user", "content": f"Evaluate and refine this LinkedIn post:\n\n{draft_output}"}
        ]
    )
    
    return message.content[0].text


# ============================================================
# RUN THE PIPELINE
# ============================================================
# Get input
if __name__ == "__main__":
    # Step 0: Generate or manual topic
    mode = input("Generate topic ideas (g) or enter your own topic (m)? ")
    if mode.lower() == "g":
        topics = generate_topics()
        print("\n--- TOPIC IDEAS ---\n")
        print(topics)
        topic = input("\nPick a topic (paste or describe it), or 'r' to regenerate: ")
        
        while topic.lower() == "r":
            print("\n💡 Generating new topics...")
            time.sleep(60)
            topics = generate_topics()
            print("\n--- TOPIC IDEAS ---\n")
            print(topics)
            topic = input("\nPick a topic (paste or describe it), or 'r' to regenerate: ")
        
        article_url = input("Any article URL to reference? (press Enter to skip): ")
        print("\n⏳ Waiting 60 seconds for rate limit...")
        time.sleep(60)

    # Step 1: Research
    if article_url:
        print("\n--- FETCHING ARTICLE ---\n")
        article_summary = fetch_article(article_url)
        print(article_summary)
        time.sleep(60)
        research_output = research(topic + "\n\nKey points from reference article:\n" + article_summary)
    else:
        research_output = research(topic)
        article_summary = None

    # Step 2: Draft variations
    drafts = draft(topic, research_output, article_summary if article_url else None)
    for i, d in enumerate(drafts):
        print(f"\n--- DRAFT VARIATION {i+1} ---\n")
        print(d)

    # Pick which draft to refine
    choice = input("\nWhich variation do you want to refine? (1/2/3): ")
    chosen_draft = drafts[int(choice) - 1]
    time.sleep(60)

    # Step 3: Refine
    final_post = refine(chosen_draft)
    print("\n--- FINAL POST ---\n")
    print(final_post)
