import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="AI Pulse", layout="wide")
st.title("🚀 AI Pulse – Newest AI Tools & Features")
st.markdown("**Real-time aggregator of the latest AI announcements, tools, models, and features** (updated live)")

# High-signal RSS feeds (curated from 2026 best sources)
FEEDS = [
    {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "Product Hunt (New AI Tools)", "url": "https://www.producthunt.com/feed"},
    {"name": "Ben's Bites (AI Tools & Launches)", "url": "https://bensbites.beehiiv.com/feed"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/"},
    {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/"},
    {"name": "arXiv cs.AI (Research)", "url": "https://rss.arxiv.org/rss/cs.AI"},
]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_all_feeds():
    all_entries = []
    progress = st.progress(0)
    for i, feed_info in enumerate(FEEDS):
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:15]:  # Limit per source to keep it fast
                published = entry.get("published_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now()
                
                summary = entry.get("summary", "")[:300] + "..." if "summary" in entry else ""
                
                all_entries.append({
                    "Source": feed_info["name"],
                    "Title": entry.title,
                    "Link": entry.link,
                    "Published": pub_date.strftime("%Y-%m-%d %H:%M"),
                    "Summary": summary
                })
        except:
            pass  # Skip broken feeds gracefully
        progress.progress((i+1)/len(FEEDS))
        time.sleep(0.2)
    
    df = pd.DataFrame(all_entries)
    if not df.empty:
        df = df.sort_values("Published", ascending=False)
        # Simple dedupe
        df = df.drop_duplicates(subset=["Title"])
    return df

if st.button("🔄 Refresh Latest AI News & Tools", type="primary"):
    with st.spinner("Fetching from 11 sources..."):
        df = fetch_all_feeds()
    
    st.success(f"✅ Found {len(df)} fresh items!")
    
    # Filters
    col1, col2 = st.columns([3,1])
    with col1:
        search = st.text_input("🔍 Search titles or keywords (e.g. 'GPT', 'Claude', 'new model')")
    with col2:
        sources = st.multiselect("Filter sources", options=FEEDS, default=["Product Hunt (New AI Tools)", "OpenAI News"])
    
    filtered = df.copy()
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False)]
    if sources:
        filtered = filtered[filtered["Source"].isin([s["name"] for s in sources])]
    
    # Display as nice cards/table
    for idx, row in filtered.iterrows():
        st.markdown(f"""
        **{row['Title']}**  
        *{row['Source']} • {row['Published']}*  
        {row['Summary']}  
        [→ Read full article]({row['Link']})
        """)
        st.divider()

else:
    st.info("Click the button above to load the latest AI news & tools!")

st.caption("Built for you by Grok • Add more feeds or AI summarization anytime")
