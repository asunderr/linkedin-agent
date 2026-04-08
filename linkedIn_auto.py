import anthropic
import time
import os
from datetime import datetime
from examples import EXAMPLE_POSTS

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"
def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except anthropic.RateLimitError:
            wait_time = 90 * (attempt + 1)
            print(f"⚠️  Rate limited. Waiting {wait_time} seconds (attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait_time)
    raise Exception("Failed after max retries due to rate limiting")

# Import your existing functions
from linkedin_pipeline import generate_topics, fetch_article, research, draft, refine

def auto_run():
    print(f"\n🚀 Auto-run starting at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # Step 0: Generate topics and pick the best one
    print("💡 Generating topics...")
    topics_text = api_call_with_retry(lambda: generate_topics())
    print("\n⏳ Waiting 60 seconds for rate limit...")
    time.sleep(60)
    
    # Ask Claude to pick the top 3 topics
    message = api_call_with_retry(lambda: client.messages.create(
        model=MODEL,
        max_tokens=512,
        system="Pick the 3 best topics from the list below. Return ONLY the topics, one per line, numbered 1-3. Nothing else.",
        messages=[
            {"role": "user", "content": f"Which of these topics would perform best on LinkedIn this week?\n\n{topics_text}"}
        ]
    ))
    top_topics = [t for t in message.content[0].text.strip().split("\n") if t.strip()][:3]
    print(f"📌 Top 3 topics selected")
    
    # Draft each topic through the full pipeline
    output_dir = os.path.expanduser("~/linkedin-drafts")
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{output_dir}/{date_str}-drafts.txt"
    
    with open(filename, "w") as f:
        f.write(f"LINKEDIN DRAFTS — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"{'='*60}\n\n")
        
        for i, topic in enumerate(top_topics):
            topic = topic.strip().lstrip("0123456789.)-– ") 
            print(f"\n🔄 Processing topic {i+1}/3: {topic[:60]}...")
            
            time.sleep(60)
            
            # Research
            research_output = research(topic)
            if len(research_output) > 3000:
                research_output = research_output[:3000]
            
            time.sleep(60)
            
            # Draft
            draft_msg = api_call_with_retry(lambda: client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system="""You are a LinkedIn ghostwriter for a senior executive — CEO-in-Residence 
at a PE fund acquiring and transforming insurance back-office service providers using AI. 
15+ years in insurance and financial services, most recently at McKinsey.

AUDIENCE: Insurance C-suite execs and PE operating partners.

POST STRUCTURE:
1. Hook: First line earns the "see more" click
2. Tension: Name a specific problem with a real number
3. The How: 3-5 concrete steps showing HOW, not just WHAT
4. Reframe: One non-obvious insight
5. CTA: Bold statement or sharp question

FORMAT: Short paragraphs. White space. 800-1200 characters. 3 hashtags max.

NON-NEGOTIABLE RULES:
- Only cite McKinsey, HBR, MIT, WSJ, Sequoia, OpenAI, Google, Anthropic.
  NEVER cite Bain, BCG, Deloitte, Accenture, PwC, EY, KPMG.
- Never fabricate case studies.
- Stay in lane: insurance ops, MGA/broker back-office, AI transformation, PE value creation.
- No AI slop.

TONE: Senior partner telling a sharp friend something interesting over drinks.""",
                messages=[
                    {"role": "user", "content": f"""Write a LinkedIn post about: {topic}

Use this research:
{research_output}

Match the voice of these examples:
{chr(10).join(f'--- EXAMPLE {j+1} ---{chr(10)}{post}' for j, post in enumerate(EXAMPLE_POSTS))}"""}
                ]
            ))
            draft_output = draft_msg.content[0].text
            
            time.sleep(60)
            
            # Refine
            final_post = api_call_with_retry(lambda: refine(draft_output))
            
            # Write to file
            f.write(f"POST {i+1}\n")
            f.write(f"TOPIC: {topic}\n")
            f.write(f"{'-'*40}\n\n")
            f.write(f"{final_post}\n\n")
            f.write(f"{'='*60}\n\n")
            
            print(f"✅ Topic {i+1} done")
    
    print(f"\n🎉 All 3 drafts saved to {filename}")
    print("Review them and pick your favorite!")
if __name__ == "__main__":
    auto_run()