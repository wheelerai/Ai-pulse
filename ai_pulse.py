import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time

# =============================================
# CONFIG & TITLE (works great on tablet)
# =============================================
st.set_page_config(page_title="AI Pulse", layout="wide", initial_sidebar_state="collapsed")
st.title("🚀 AI Pulse – Newest AI Tools & Features")
st.markdown("**Real-time aggregator of the latest AI news, models, tools & features** (refreshes live)")

# =============================================
# FEEDS (you can add more later)
# =============================================
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

# Extract just the names for the multiselect (this fixes the crash)
feed_names = [f["name"] for f in FEEDS]st.write("Available sources:", feed_names)   # ← add this

# =============================================
# FETCH FUNCTION (cached)
# =============================================
@st.cache_data(ttl=3600)  # 1 hour cache
def fetch_all_feeds():
    all_entries = []
    progress = st.progress(0)
    
    for i, feed_info in enumerate(FEEDS):
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:15]:
                published = entry.get("published_parsed")
                pub_date = datetime(*published[:6]) if published else datetime.now()
                
                summary = entry.get("summary", "")[:280]
                if len(summary) == 280:
                    summary += "..."
                
                all_entries.append({
                    "Source": feed_info["name"],
                    "Title": entry.title,
                    "Link": entry.link,
                    "Published": pub_date.strftime("%Y-%m-%d %H:%M"),
                    "Summary": summary
                })
        except:
            pass  # skip broken feed
        progress.progress((i + 1) / len(FEEDS))
        time.sleep(0.1)
    
    df = pd.DataFrame(all_entries)
    if not df.empty:
        df = df.sort_values("Published", ascending=False)
        df = df.drop_duplicates(subset=["Title"])
    return df

# =============================================
# UI
# =============================================
if st.button("🔄 Refresh Latest AI News & Tools", type="primary", use_container_width=True):
    with st.spinner("Fetching from 11 sources..."):
        df = fetch_all_feeds()
    
    st.success(f"✅ Found {len(df)} fresh items!")

    # Search (full width on tablet)
    search = st.text_input("🔍 Search titles or keywords (e.g. 'GPT', 'Claude', 'new model')", placeholder="Type here...")

    # FIXED multiselect – uses string names only (this was the crash)
    selected_sources = st.multiselect(
        "Filter sources",
        options=feed_names,
        default=["Product Hunt (New AI Tools)", "OpenAI News", "Ben's Bites (AI Tools & Launches)"]
    )

    # Filter the data
    filtered = df.copy()
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]
    if selected_sources:
        filtered = filtered[filtered["Source"].isin(selected_sources)]

    # Display as clean cards (mobile-friendly)
    if filtered.empty:
        st.warning("No results found. Try different search or filters.")
    else:
        for _, row in filtered.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Title']}**")
                st.caption(f"*{row['Source']} • {row['Published']}*")
                st.write(row['Summary'])
                st.markdown(f"[→ Read full article]({row['Link']})", unsafe_allow_html=True)
            st.divider()

else:
    st.info("👆 Click the Refresh button above to load the latest AI tools & news!")
    st.caption("Built for you • Works perfectly on Android tablet")

st.caption("💡 Tip: Add to home screen in Chrome for app-like feel")
