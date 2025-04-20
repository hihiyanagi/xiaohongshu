import requests
import json

def test_html_api():
    """Test the Xiaohongshu API with direct HTML input"""
    
    # Sample HTML content with meta tags as provided in the example
    html_content = """
    <html>
    <head>
        <meta property="og:title" content="11/8我的爵士三重奏在荻窪velvet sun演出 - 小红书">
        <meta name="description" content="open 7:15- start 8:00- 	 欢迎朋友们来聚！ 	 【profile】 賀　悦航 2002年生まれ、中国長沙市出身。5歳からクラシックピアノを始め。17歳の頃、日本でジャズと出会う。2020年国立音楽大学ジャズ専修入学、ジャズピアノを塩谷哲氏、小曽根真氏、熊谷ヤスマサ氏、宮本貴奈氏に師氏。2023年度爵士高手争霸赛(中国全国ジャズコンクール)第二位。2024年、矢田部賞を受賞し国立音楽大学ジャズ専修を首席で卒業。今は都内を中心にライブなどの音楽活動を行っている。 廣橋　契 1999年生まれ、千葉県千葉市出身。幼少期は教会の合唱隊に所属、讃美歌やゴスペル音楽を身近に聴いて育つ。中学生からアコースティックギターを独学で習得。千葉市にあるインターナショナルスクールCovenant Community School Internationalを卒業後、2018年国際基督教大学入学と同時に同大学ビッグバンド、モダンミュージックソサイエティに入部、コントラバスとジャズに出会う。以来、都内の大学・セッションバー・ライブハウスなどに足しげく通い、演奏経験を積む。2022年度は、国立音楽大学Newtide Jazz Orchestraのメンバーとしても活動。ジャズベースを楠井五月氏に師事。大学卒業後は、都内を中心にライブやセッションなどの演奏活動を行っている。 塚田　陽太 2000年、神奈川県横浜市生まれ。 8歳よりドラムをはじめ、岡村タカオ氏に師事する。ジャズドラマーである岡村氏の影響を受け徐々にジャズに傾倒。 2018年、昭和音楽大学ジャズコースに入学。 小山太郎氏に師事する。 2022年、同学を優等賞を受賞し卒業。 またこれまでに2度、米カリフォルニア州のCalifornia Jazz Conservatoryでの短期留学プログラムに参加し、現地の人々や音楽との交流を深める。 現在は自身のトリオをはじめ安ヵ川大樹(ba)ニュートリオなどのグループで都内・横浜を中心に活動中。 	 #小屁孩  #爵士 #爵士钢琴 #演出 #日本爵士 #日本音乐 #当代爵士">
        <meta property="og:image" content="http://sns-webpic-qc.xhscdn.com/202504201151/e96dff44098d5da76080cb3e1c6c85cb/1040g2sg319mtv65t7g104a3kbqgkjf706lcmbhg!nd_dft_wlteh_webp_3">
        <meta property="og:image" content="http://sns-webpic-qc.xhscdn.com/202504201151/60d6370af4adfec0bede62851268f112/1040g2sg319mtv65t7g1g4a3kbqgkjf708iivju0!nd_dft_wgth_webp_3">
    </head>
    <body>
        <h1>Page Content</h1>
    </body>
    </html>
    """
    
    # API endpoint (assuming the FastAPI app is running locally)
    api_url = "http://localhost:8000/parse-html"
    
    # Prepare the request payload
    payload = {
        "html_content": html_content,
        "use_meta_tags": True
    }
    
    # Send the request to the API
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Parse the response
        data = response.json()
        
        # Print the results
        print("\n===== API RESPONSE =====")
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print("\n===== CONTENT =====")
        print(f"Title: {data['title']}")
        
        print("\nContent paragraphs:")
        for i, paragraph in enumerate(data['content'], 1):
            print(f"{i}. {paragraph}")
        
        print("\nImages:")
        for i, image in enumerate(data['images'], 1):
            print(f"{i}. {image}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_html_api() 