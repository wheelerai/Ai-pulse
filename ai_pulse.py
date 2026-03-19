import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="AI Pulse", layout="wide", initial_sidebar_state="collapsed")
st.title("🚀 AI Pulse – Newest AI Tools & Features")
st.markdown("**Real-time aggregator of the latest AI news, models, tools & features**")

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

feed_names = [f["name"] for f in FEEDS]

# Temporary debug (you can delete this line later)
st.write("✅ Available sources:", feed_names)

@st.cache_data(ttl=3600)
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
                if len(summary) == 280: summary += "..."
                all_entries.append({
                    "Source": feed_info["name"],
                    "Title": entry.title,
                    "Link": entry.link,
                    "Published": pub_date.strftime("%Y-%m-%d %H:%M"),
                    "Summary": summary
                })
        except:
            pass
        progress.progress((i + 1) / len(FEEDS))
        time.sleep(0.1)
    df = pd.DataFrame(all_entries)
    if not df.empty:
        df = df.sort_values("Published", ascending=False).drop_duplicates(subset=["Title"])
    return df

if st.button("🔄 Refresh Latest AI News & Tools", type="primary", use_container_width=True):
    with st.spinner("Fetching from 11 sources..."):
        df = fetch_all_feeds()
    
    st.success(f"✅ Found {len(df)} fresh items!")

    search = st.text_input("🔍 Search titles or keywords (e.g. 'GPT', 'Claude', 'new model')")

    # SAFE multiselect — this fixes the crash forever
    selected_sources = st.multiselect(
        "Filter sources",
        options=feed_names,
        default=feed_names[:3],   # always safe (first 3 sources)
        placeholder="Choose sources to filter"
    )

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]
    if selected_sources:
        filtered = filtered[filtered["Source"].isin(selected_sources)]

    if filtered.empty:
        st.warning("No results — try a different search or filters.")
    else:
        for _, row in filtered.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Title']}**")
                st.caption(f"*{row['Source']} • {row['Published']}*")
                st.write(row['Summary'])
                st.markdown(f"[→ Read full article]({row['Link']})", unsafe_allow_html=True)
            st.divider()

else:
    st.info("👆 Click the big Refresh button above to start!")
    st.caption("Works perfectly on Android tablet")

st.caption("💡 Add this page to your home screen in Chrome for app-like feel")
