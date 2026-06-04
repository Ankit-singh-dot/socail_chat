import os
import json
import csv

def generate():
    os.makedirs("data_exports", exist_ok=True)
    
    # 1. Twitter
    twitter_data = [
        {"tweet": {"id_str": "1", "created_at": "Mon Jan 10 14:00:00 +0000 2023", "full_text": "I think building a normalization layer is the most underrated part of data engineering. Standardize your schema early! #data"}},
        {"tweet": {"id_str": "2", "created_at": "Tue Feb 15 09:30:00 +0000 2023", "full_text": "RT @someone: retweets should be ignored by the parser."}},
        {"tweet": {"id_str": "3", "created_at": "Wed Mar 01 10:15:00 +0000 2023", "full_text": "The transition from OpenAI to local models is going to accelerate this year. Being locked into one vendor is too risky for production pipelines."}},
        {"tweet": {"id_str": "4", "created_at": "Fri Apr 14 18:20:00 +0000 2023", "full_text": "Next.js is great, but sometimes I miss the simplicity of just writing plain HTML and vanilla JS. The frontend ecosystem moves too fast."}},
        {"tweet": {"id_str": "5", "created_at": "Sun May 07 20:00:00 +0000 2023", "full_text": "Vector databases are just the beginning. The real challenge in RAG is chunking strategies and metadata filtering, not just the embedding model."}}
    ]
    with open("data_exports/mock_twitter.json", "w") as f:
        json.dump(twitter_data, f)
        
    # 2. LinkedIn
    linkedin_data = [
        ["Date", "ShareCommentary", "ShareLink"],
        ["2023-01-10 14:00:00", "Remote work has fundamentally changed how we build systems. The latency of communication forces better documentation.", "https://linkedin.com/post/1"],
        ["2023-02-15 09:30:00", "I really enjoy using Qdrant for vector search. The metadata filtering is unmatched compared to Chroma.", "https://linkedin.com/post/2"],
        ["2023-06-20 11:45:00", "Just passed my AWS Solutions Architect exam! The hardest part was definitely the networking scenarios. Proud of this milestone.", "https://linkedin.com/post/3"],
        ["2023-08-12 16:10:00", "Hiring tip: I don't look at LeetCode scores. I look at how you structure a small project, how you write commits, and if you can explain your architectural tradeoffs.", "https://linkedin.com/post/4"],
        ["2023-11-05 09:00:00", "We are migrating our entire stack to Kubernetes next month. If anyone has tips on managing Helm charts at scale, please drop them below!", "https://linkedin.com/post/5"]
    ]
    with open("data_exports/mock_linkedin.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(linkedin_data)
        
    # 3. Instagram
    instagram_html = """
    <html><body>
        <div class="pam _3-95 _2pi0 _2lej uiBoxWhite noborder">
            <div class="_3-94 _2lem">Here is a picture of my new mechanical keyboard setup! Loving the tactile switches. #workspace</div>
            <div class="_3-94 _2lem">2023-09-15T12:00:00</div>
        </div>
        <div class="pam _3-95 _2pi0 _2lej uiBoxWhite noborder">
            <div class="_3-94 _2lem">Hiking in the mountains today. Unplugging from technology is the best way to prevent burnout.</div>
            <div class="_3-94 _2lem">2023-10-22T14:30:00</div>
        </div>
        <div class="pam _3-95 _2pi0 _2lej uiBoxWhite noborder">
            <div class="_3-94 _2lem">Made the best homemade pizza last night. The secret is letting the dough ferment for 48 hours! 🍕</div>
            <div class="_3-94 _2lem">2023-12-05T19:45:00</div>
        </div>
    </body></html>
    """
    with open("data_exports/mock_instagram.html", "w") as f:
        f.write(instagram_html)
        
if __name__ == "__main__":
    generate()
    print("Generated rich mock data in data_exports/")
