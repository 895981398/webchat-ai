"""
智能回复引擎
基于关键词和规则生成回复
"""

import json
import os
import random
from datetime import datetime

class ReplyEngine:
    """回复引擎 - 生成智能回复"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.rules = self._load_rules()
        
        # 基础回复规则
        self.base_rules = {
            'greeting': {
                'keywords': ['你好', 'hello', 'hi', '在吗', '哈喽', '嗨'],
                'responses': ['你好！', '嗨！', '在的，有什么事吗？', '你好呀～']
            },
            'thanks': {
                'keywords': ['谢谢', '感谢', '多谢', 'thank', 'thanks'],
                'responses': ['不客气！', '应该的', '很高兴能帮到你', '不用谢～']
            },
            'time': {
                'keywords': ['时间', '几点', '现在几点', '几点了'],
                'responses': ['现在是{time}', '现在{time}了', '当前时间: {time}']
            },
            'weather': {
                'keywords': ['天气', '下雨', '晴天', '温度', '冷', '热'],
                'responses': ['今天天气不错', '可以查一下天气预报', '天气挺好的']
            },
            'work': {
                'keywords': ['工作', '项目', '任务', '进度', 'deadline', '截止'],
                'responses': ['工作正在推进中', '项目进度正常', '任务已完成']
            },
            'question': {
                'keywords': ['吗', '？', '?', '如何', '怎么', '为什么'],
                'responses': ['这个问题需要具体分析', '我可以帮你查一下', '让我想想怎么回答']
            },
            'default': {
                'responses': ['嗯，我在听', '好的', '明白了', '收到']
            }
        }
        
    def _load_rules(self):
        """加载规则配置"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules')
        rules_file = os.path.join(rules_dir, 'reply_rules.json')
        
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        else:
            # 创建默认规则文件
            default_rules = {
                'rules': {},
                'templates': {}
            }
            os.makedirs(rules_dir, exist_ok=True)
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(default_rules, f, ensure_ascii=False, indent=2)
            return {}
            
    def generate_reply(self, message_data):
        """
        生成回复
        
        Args:
            message_data: 消息数据字典
                - content: 消息内容
                - username: 发送者ID
                - sender: 实际发送者（群聊时）
                - timestamp: 时间戳
                
        Returns:
            str: 生成的回复
        """
        content = message_data.get('content', '').lower()
        username = message_data.get('username', '')
        
        print(f"[ReplyEngine] 处理消息: {content[:50]}...")
        
        # 1. 检查是否有特定回复规则
        specific_reply = self._check_specific_rules(content, username)
        if specific_reply:
            return specific_reply
            
        # 2. 关键词匹配
        matched_rule = self._match_keywords(content)
        if matched_rule:
            return self._get_response_from_rule(matched_rule)
            
        # 3. 默认回复
        return self._get_default_response()
        
    def _check_specific_rules(self, content, username):
        """检查特定回复规则"""
        # 可以根据用户名或特定内容设置特殊规则
        # 例如：对特定联系人或群聊使用特定回复
        
        # 这里可以添加特定规则
        # if username == "特定联系人":
        #     return "特定回复"
            
        return None
        
    def _match_keywords(self, content):
        """关键词匹配"""
        matched_rules = []
        
        for rule_name, rule_data in self.base_rules.items():
            if 'keywords' in rule_data:
                for keyword in rule_data['keywords']:
                    if keyword in content:
                        matched_rules.append(rule_name)
                        break
                        
        if matched_rules:
            # 返回第一个匹配的规则
            return matched_rules[0]
            
        # 如果没有匹配，检查是否是疑问句
        if any(q in content for q in ['吗', '？', '?', '如何', '怎么']):
            return 'question'
            
        return None
        
    def _get_response_from_rule(self, rule_name):
        """根据规则获取回复"""
        rule_data = self.base_rules.get(rule_name)
        if not rule_data or 'responses' not in rule_data:
            return self._get_default_response()
            
        responses = rule_data['responses']
        reply = random.choice(responses)
        
        # 处理占位符
        if '{time}' in reply:
            current_time = datetime.now().strftime("%H:%M")
            reply = reply.replace('{time}', current_time)
            
        return reply
        
    def _get_default_response(self):
        """获取默认回复"""
        default_responses = self.base_rules.get('default', {}).get('responses', ['嗯，我在听'])
        return random.choice(default_responses)
        
    def add_rule(self, rule_name, keywords, responses):
        """添加新规则（供学习使用）"""
        if rule_name not in self.base_rules:
            self.base_rules[rule_name] = {
                'keywords': keywords,
                'responses': responses
            }
            print(f"[ReplyEngine] 添加新规则: {rule_name}")
            return True
        return False
        
    def learn_from_conversation(self, question, answer):
        """从对话中学习"""
        # 后续可以添加学习功能
        pass