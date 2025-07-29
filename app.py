
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

st.set_page_config(
    page_title="AI Review Trend Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import Config
from src.data_collector import ReviewDataCollector
from src.report_generator import TrendReportGenerator

def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin: 1rem 0;
        padding: 0.5rem;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    st.markdown('<h1 class="main-header">🤖 AI Review Trend Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by Agentic AI • Built for Pulsegen Technologies</p>', unsafe_allow_html=True)
    
  
    with st.sidebar:
        st.header("⚙️ Configuration")
       
        app_options = {
            "Amazon Shopping": "com.amazon.mShop.android.shopping",
            "Zomato": "com.application.zomato",
            "Prime Video": "com.amazon.avod.thirdpartyclient",
            "Amazon Music": "com.amazon.mp3"
        }
        
        selected_app = st.selectbox(
            "📱 Select App to Analyze",
            list(app_options.keys()),
            index=0
        )
        
        app_id = app_options[selected_app]
        
        
        st.subheader("📅 Date Range")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=2),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime.now() - timedelta(days=1),
                max_value=datetime.now()
            )
        
       
        if start_date > end_date:
            st.error("Start date must be before end date!")
            return
        
     
        st.subheader("🔧 Analysis Settings")
        batch_size = st.slider("Batch Size (reviews per LLM call)", 5, 20, 10)
        
    
        st.subheader("🔑 API Status")
        config = Config()
        
        openai_status = "✅ Connected" if config.OPENAI_API_KEY else "❌ Missing"
        scraper_status = "✅ Connected" if config.SCRAPER_API_KEY else "❌ Missing"
        
        st.write(f"OpenAI API: {openai_status}")
        st.write(f"Scraper API: {scraper_status}")
        
        if not config.OPENAI_API_KEY:
            st.error("⚠️ OpenAI API key required!")
            return
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: right; padding: 7px; margin-top: 8rem; font-size: 14px; color: #008000;'>
            <p>🤖 Built by<br><strong>Prathamesh J. Pawar</strong></p>
            <p>© 2025</p>
        </div>
        """, unsafe_allow_html=True)

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Analysis", "📊 Results", "📈 Visualizations", "💾 Data"])
    
    with tab1:
        st.markdown('<div class="sub-header">🚀 Run Analysis</div>', unsafe_allow_html=True)
        
        # Display configuration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📱 App</h3>
                <p><strong>{selected_app}</strong></p>
                <small>{app_id}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            days_diff = (end_date - start_date).days + 1
            st.markdown(f"""
            <div class="metric-card">
                <h3>📅 Duration</h3>
                <p><strong>{days_diff} days</strong></p>
                <small>{start_date} to {end_date}</small>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚙️ Settings</h3>
                <p><strong>Batch: {batch_size}</strong></p>
                <small>AI-powered analysis</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Run analysis button
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            run_analysis(selected_app, app_id, start_date, end_date, batch_size)
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_visualizations_tab()
        
    with tab4:
        show_data_tab()

        

def run_analysis(app_name, app_id, start_date, end_date, batch_size):
    """Run the complete analysis pipeline with progress tracking"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Data Collection (20% progress)
        status_text.text("📊 Step 1/4: Collecting review data...")
        progress_bar.progress(0.05)
        
        collector = ReviewDataCollector()
        
        # Update config temporarily
        config = Config()
        config.TARGET_APP_ID = app_id
        config.APP_NAME = app_name
        collector.config = config
        
        total_reviews = 0
        collection_results = []
        
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            status_text.text(f"📅 Collecting reviews for {date_str}...")
            
            reviews = collector.collect_daily_reviews_gps(app_id, date_str)
            if reviews:
                collector.save_daily_data(reviews, date_str)
                total_reviews += len(reviews)
                collection_results.append({"date": date_str, "count": len(reviews)})
            
            current += timedelta(days=1)
        
        progress_bar.progress(0.2)
        
        if total_reviews == 0:
            st.error("❌ No reviews found for the selected date range!")
            return
        
        st.success(f"✅ Collected {total_reviews} reviews across {len(collection_results)} days")
        
        # Step 2: AI Analysis (60% progress)
        status_text.text("🤖 Step 2/4: Running AI analysis...(It will take 4-5min according to data)")
        progress_bar.progress(0.25)
        
        generator = TrendReportGenerator(batch_size=batch_size)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Run with progress updates
        trend_df = generator.generate_trend_table_range(start_str, end_str)
        progress_bar.progress(0.85)
        
        if trend_df.empty:
            st.error("❌ No topics generated. Check your API keys and data.")
            return
        
        # Step 3: Save Results (95% progress)
        status_text.text("💾 Step 3/4: Saving results...")
        progress_bar.progress(0.9)
        
        # Save reports
        csv_file = generator.save_report(trend_df, start_str, end_str, fmt="csv")
        excel_file = generator.save_report(trend_df, start_str, end_str, fmt="xlsx")
        
        # Step 4: Complete (100% progress)
        status_text.text("✅ Analysis completed successfully!")
        progress_bar.progress(1.0)
        
        # Store results in session state
        st.session_state['analysis_results'] = {
            'trend_df': trend_df,
            'total_reviews': total_reviews,
            'app_name': app_name,
            'date_range': f"{start_str} to {end_str}",
            'csv_file': csv_file,
            'excel_file': excel_file,
            'collection_results': collection_results
        }
        
        # Success message
        st.markdown(f"""
        <div class="success-box">
            <h3>🎉 Analysis Complete!</h3>
            <p>✅ <strong>{total_reviews}</strong> reviews analyzed</p>
            <p>📊 <strong>{len(trend_df)}</strong> topics identified</p>
            <p>💾 Reports saved to <code>output/</code> folder</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show quick preview
        st.subheader("📋 Quick Preview - Top 10 Topics")
        st.dataframe(trend_df.head(10), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        progress_bar.progress(0)

def show_results_tab():
    """Display analysis results"""
    
    if 'analysis_results' not in st.session_state:
        st.info("👆 Run an analysis first to see results here!")
        return
    
    results = st.session_state['analysis_results']
    trend_df = results['trend_df']
    
    st.markdown('<div class="sub-header">📊 Analysis Results</div>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📱 App", results['app_name'])
    
    with col2:
        st.metric("📊 Total Reviews", results['total_reviews'])
    
    with col3:
        st.metric("🏷️ Topics Found", len(trend_df))
    
    with col4:
        date_cols = [col for col in trend_df.columns if col != 'Topic']
        total_mentions = trend_df[date_cols].sum().sum()
        st.metric("💬 Total Mentions", total_mentions)
    
    st.markdown("---")
    
    # Full results table
    st.subheader("📋 Complete Trend Analysis Table")
    
    # Add search and filter options
    search_term = st.text_input("🔍 Search topics:", placeholder="e.g., delivery, payment, app crash")
    
    if search_term:
        filtered_df = trend_df[trend_df['Topic'].str.contains(search_term, case=False, na=False)]
        st.write(f"Found {len(filtered_df)} topics matching '{search_term}'")
    else:
        filtered_df = trend_df
    
    # Display table with formatting
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )
    
    # Download buttons
    st.subheader("💾 Download Reports")
    col1, col2 = st.columns(2)
    
    with col1:
        if results.get('csv_file') and os.path.exists(results['csv_file']):
            with open(results['csv_file'], 'rb') as f:
                st.download_button(
                    "📄 Download CSV",
                    data=f.read(),
                    file_name=f"trend_report_{results['date_range']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col2:
        if results.get('excel_file') and os.path.exists(results['excel_file']):
            with open(results['excel_file'], 'rb') as f:
                st.download_button(
                    "📊 Download Excel",
                    data=f.read(),
                    file_name=f"trend_report_{results['date_range']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

def show_visualizations_tab():
    """Display interactive visualizations"""
    
    if 'analysis_results' not in st.session_state:
        st.info("👆 Run an analysis first to see visualizations here!")
        return
    
    results = st.session_state['analysis_results']
    trend_df = results['trend_df']
    
    st.markdown('<div class="sub-header">📈 Interactive Visualizations</div>', unsafe_allow_html=True)
    
    if trend_df.empty:
        st.warning("No data to visualize.")
        return
    
    # Get date columns
    date_cols = [col for col in trend_df.columns if col != 'Topic']
    
    # 1. Top Topics Bar Chart
    st.subheader("🔥 Top 10 Trending Topics")
    
    top_10 = trend_df.head(10).copy()
    top_10['Total'] = top_10[date_cols].sum(axis=1)
    
    fig_bar = px.bar(
        top_10,
        x='Total',
        y='Topic',
        orientation='h',
        title="Most Mentioned Topics",
        color='Total',
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 2. Trend Lines
    st.subheader("📈 Topic Trends Over Time")
    
    # Select topics for trend analysis
    selected_topics = st.multiselect(
        "Select topics to compare:",
        options=trend_df['Topic'].head(10).tolist(),
        default=trend_df['Topic'].head(5).tolist()
    )
    
    if selected_topics:
        # Prepare data for line chart
        trend_data = []
        for topic in selected_topics:
            topic_row = trend_df[trend_df['Topic'] == topic].iloc[0]
            for date_col in date_cols:
                trend_data.append({
                    'Date': date_col,
                    'Topic': topic,
                    'Mentions': topic_row[date_col]
                })
        
        trend_viz_df = pd.DataFrame(trend_data)
        
        fig_line = px.line(
            trend_viz_df,
            x='Date',
            y='Mentions',
            color='Topic',
            title="Topic Trends Over Time",
            markers=True
        )
        fig_line.update_layout(height=500)
        st.plotly_chart(fig_line, use_container_width=True)
    
    # 3. Heatmap
    st.subheader("🗺️ Topic Intensity Heatmap")
    
    # Prepare heatmap data (top 15 topics)
    heatmap_data = trend_df.head(15)[['Topic'] + date_cols].set_index('Topic')
    
    fig_heatmap = px.imshow(
        heatmap_data.values,
        x=date_cols,
        y=heatmap_data.index,
        title="Topic Mentions Intensity",
        color_continuous_scale='Blues',
        aspect='auto'
    )
    fig_heatmap.update_layout(height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 4. Daily Review Volume
    if 'collection_results' in results:
        st.subheader("📊 Daily Review Collection Volume")
        
        collection_df = pd.DataFrame(results['collection_results'])
        
        fig_volume = px.bar(
            collection_df,
            x='date',
            y='count',
            title="Reviews Collected Per Day",
            color='count',
            color_continuous_scale='blues'
        )
        fig_volume.update_layout(height=400)
        st.plotly_chart(fig_volume, use_container_width=True)

def show_data_tab():
    """Display raw data and system information"""
    
    st.markdown('<div class="sub-header">💾 Data & System Info</div>', unsafe_allow_html=True)
    
    # System information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 System Configuration")
        config = Config()
        
        st.code(f"""
App ID: {getattr(config, 'TARGET_APP_ID', 'Not set')}
App Name: {getattr(config, 'APP_NAME', 'Not set')}
Batch Size: {getattr(config, 'BATCH_SIZE', 10)}
OpenAI API: {'✅ Configured' if config.OPENAI_API_KEY else '❌ Missing'}
Scraper API: {'✅ Configured' if config.SCRAPER_API_KEY else '❌ Missing'}
        """)

        
    
    with col2:
        st.subheader("📁 Data Files")
        
        # Check for existing data files
        data_dir = Path("data/raw_reviews")
        if data_dir.exists():
            data_files = list(data_dir.glob("*.json"))
            st.write(f"Found {len(data_files)} data files:")
            
            for file in sorted(data_files)[-10:]:  # Show last 10 files
                file_size = file.stat().st_size / 1024  # Size in KB
                st.write(f"📄 {file.name} ({file_size:.1f} KB)")
        else:
            st.write("No data files found.")
    
    # Raw data preview
    if 'analysis_results' in st.session_state:
        st.subheader("📋 Raw Analysis Data")
        
        results = st.session_state['analysis_results']
        
        # Show full dataframe
        st.write("Complete trend analysis table:")
        st.dataframe(results['trend_df'], use_container_width=True)
        
        # Export raw data as JSON
        json_data = results['trend_df'].to_json(orient='records', indent=2)
        st.download_button(
            "📦 Download Raw JSON Data",
            data=json_data,
            file_name=f"raw_data_{results['date_range']}.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
