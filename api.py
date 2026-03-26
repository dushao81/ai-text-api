#!/usr/bin/env python3
"""
AI文本处理API服务
功能：文本摘要、关键词提取、情感分析、格式转换
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
from urllib.parse import urlparse, parse_qs

PORT = 8888

class TextHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self.send_json({
                'name': 'AI文本处理API',
                'version': '1.0',
                'endpoints': [
                    '/api/summarize?text=xxx - 文本摘要',
                    '/api/keywords?text=xxx - 关键词提取',
                    '/api/sentiment?text=xxx - 情感分析',
                    '/api/wordcount?text=xxx - 字数统计'
                ]
            })
        elif path == '/api/wordcount':
            params = parse_qs(parsed.query)
            text = params.get('text', [''])[0]
            words = len(text)
            chars = len(text.replace(' ', ''))
            self.send_json({'words': words, 'chars': chars, 'lines': len(text.split('\n'))})
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/summarize':
            text = data.get('text', '')
            result = self.summarize(text)
            self.send_json({'summary': result})
        elif path == '/api/keywords':
            text = data.get('text', '')
            result = self.extract_keywords(text)
            self.send_json({'keywords': result})
        elif path == '/api/sentiment':
            text = data.get('text', '')
            result = self.analyze_sentiment(text)
            self.send_json(result)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def summarize(self, text):
        """简单摘要：提取前两句 + 最后一句"""
        if not text:
            return ''
        sentences = re.split(r'[。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= 3:
            return text
        return sentences[0] + '。' + sentences[-1]
    
    def extract_keywords(self, text):
        """简单关键词提取：统计高频词"""
        if not text:
            return []
        # 移除标点，统计词频
        words = re.findall(r'[\w]{2,}', text.lower())
        word_count = {}
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '我', '你', '他', '她', '它', '们', '这', '那', '有', '没有', '一个', '可以'}
        for word in words:
            if word not in stopwords and len(word) >= 2:
                word_count[word] = word_count.get(word, 0) + 1
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:10]]
    
    def analyze_sentiment(self, text):
        """简单情感分析：基于关键词"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0}
        positive = ['好', '棒', '赞', '优秀', '出色', '喜欢', '满意', '开心', '高兴', '完美', '太棒', '厉害']
        negative = ['差', '烂', '糟', '失望', '不满', '讨厌', '难过', '糟糕', '无语', '气愤', '垃圾', '坑']
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        score = (pos_count - neg_count) / max(len(text), 1) * 100
        if score > 0.5:
            return {'sentiment': 'positive', 'score': round(score, 2)}
        elif score < -0.5:
            return {'sentiment': 'negative', 'score': round(abs(score), 2)}
        return {'sentiment': 'neutral', 'score': 0}

def run():
    server = HTTPServer(('', PORT), TextHandler)
    print(f'AI文本处理API已启动 http://localhost:{PORT}')
    print('endpoints: /api/summarize, /api/keywords, /api/sentiment, /api/wordcount')
    server.serve_forever()

if __name__ == '__main__':
    run()
