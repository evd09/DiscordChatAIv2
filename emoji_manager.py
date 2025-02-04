import random

class EmojiManager:
    def __init__(self):
        self.EMOJI_CATEGORIES = {
            'happy': ['😊', '😄', '😃', '🥰', '😘', '😋', '😍', '🤗', '🌟', '✨', '💫', '⭐', '😁', '😸', '😺'],
            'sad': ['😢', '😭', '🥺', '😔', '😪', '💔', '😿', '🫂', '🥀', '😕', '😓', '😩'],
            'playful': ['😜', '🤪', '😝', '😋', '🤭', '🙈', '🙉', '🙊', '🐱', '🐰', '🦊', '🐼', '🦝', '🐨', '🐯'],
            'cool': ['😎', '🕶️', '🔥', '💯', '🆒', '🤙', '👑', '💪', '✌️', '🎮', '🎯', '🎪', '🌟', '⚡', '🌈'],
            'love': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🤍', '🖤', '💝', '💖', '💗', '💓', '💕', '💞', '💘'],
            'spooky': ['💀', '👻', '🎃', '🦇', '🕷️', '🕸️', '🧟‍♂️', '🧟‍♀️', '👺', '👹', '😈', '🤡', '🌚', '🦴', '☠️'],
            'thinking': ['🤔', '🧐', '💭', '💡', '🎯', '📚', '🔍', '💻', '📝', '🎓', '🧮', '📊'],
            'misc': ['🌈', '🎨', '🎭', '🎪', '🎡', '🎢', '🎠', '🌸', '🌺', '🌷', '🌹', '🍀', '🌙', '⭐', '🌟'],
            'food': ['🍜', '🍱', '🍣', '🍙', '🍡', '🍵', '🧋', '🍰', '🍪', '🍩', '🍦', '🍭'],
            'magic': ['✨', '💫', '🌟', '⭐', '🔮', '🎭', '🎪', '🎇', '🎆', '🪄', '🧙‍♀️', '🧙‍♂️'],
            'nature': ['🌸', '🌺', '🌷', '🌹', '🌱', '🌲', '🍀', '🌿', '🍃', '🌾', '🌻', '🌼'],
            'tech': ['💻', '📱', '⌨️', '🖥️', '🎮', '🕹️', '🤖', '👾', '💾', '📡', '🔌', '💡']
        }
        
        self.SENTIMENT_MAPPING = {
            'happy': ['happy', 'great', 'awesome', 'wonderful', 'yay', 'good', 'nice', 'excellent'],
            'sad': ['sad', 'sorry', 'unfortunate', 'bad', 'wrong', 'error', 'fail', 'mistake'],
            'love': ['love', 'heart', 'care', 'sweet', 'cute', 'adorable', 'precious'],
            'thinking': ['think', 'question', 'how', 'what', 'why', 'learn', 'study', 'curious'],
            'playful': ['fun', 'play', 'game', 'lol', 'haha', 'joke', 'silly', 'funny'],
            'cool': ['cool', 'awesome', 'nice', 'amazing', 'wow', 'impressive', 'sick'],
            'spooky': ['spooky', 'scary', 'halloween', 'ghost', 'dead', 'monster', 'creepy'],
            'tech': ['code', 'program', 'computer', 'tech', 'bot', 'digital', 'online'],
            'magic': ['magic', 'special', 'wonderful', 'amazing', 'mysterious', 'fantasy'],
            'nature': ['nature', 'flower', 'tree', 'plant', 'garden', 'grow', 'bloom']
        }

    def analyze_message_sentiment(self, content):
        """Analyze message content and return relevant emoji categories"""
        content = content.lower()
        matched_categories = set()
        
        # Check content against each sentiment category
        for category, keywords in self.SENTIMENT_MAPPING.items():
            if any(keyword in content for keyword in keywords):
                matched_categories.add(category)
        
        # Always include some default categories if nothing matches
        if not matched_categories:
            matched_categories = {'happy', 'misc', 'playful'}
        
        # Add 'misc' category for additional variety
        matched_categories.add('misc')
        
        return matched_categories

    def get_random_emojis(self, categories, num_emojis=3):
        """Get random emojis from specified categories"""
        all_relevant_emojis = []
        for category in categories:
            all_relevant_emojis.extend(self.EMOJI_CATEGORIES.get(category, []))
        
        # Ensure we don't try to get more emojis than we have
        num_emojis = min(num_emojis, len(all_relevant_emojis))
        
        return random.sample(all_relevant_emojis, num_emojis)

    def get_error_emojis(self):
        """Get error-specific emojis"""
        return random.sample(self.EMOJI_CATEGORIES['sad'] + self.EMOJI_CATEGORIES['thinking'], 2)