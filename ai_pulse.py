import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="AI Pulse", layout="wide", initial_sidebar_state="collapsed")
st.title("🚀 AI Pulse – Newest AI Tools & Features")
st.markdown("**Real-time aggregator • Earn with every click**")

FEEDS = [ ... ]  # Keep your exact FEEDS list from before (no change needed)

feed_names = [f["name"] for f in FEEDS]

@st.cache_data(ttl=3600)
def fetch_all_feeds():
    # Same fetch function as before — unchanged
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

    search = st.text_input("🔍 Search titles or keywords")
    selected_sources = st.multiselect("Filter sources", options=feed_names, default=feed_names[:3])

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["Title"].str.contains(search, case=False, na=False)]
    if selected_sources:
        filtered = filtered[filtered["Source"].isin(selected_sources)]

    # MONETIZATION: Export button for newsletter
    if st.button("📥 Export Top 10 for Newsletter (CSV)"):
        csv = filtered.head(10).to_csv(index=False)
        st.download_button("⬇️ Download CSV Now", csv, "ai_pulse_top10.csv", "text/csv")

    if filtered.empty:
        st.warning("No results — try different filters.")
    else:
        for _, row in filtered.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Title']}**")
                st.caption(f"*{row['Source']} • {row['Published']}*")
                st.write(row['Summary'])
                st.markdown(f"[→ Read full article]({row['Link']})  •  [Try Cursor AI](https://cursor.com/?ref=yourname)  •  [Try Perplexity](https://perplexity.ai/?ref=yourname)", unsafe_allow_html=True)
            st.divider()

else:
    st.info("👆 Click Refresh to load the latest AI news!")
    st.caption("Add to home screen for app feel")

st.caption("💰 Your app now earns when people click the tools")
