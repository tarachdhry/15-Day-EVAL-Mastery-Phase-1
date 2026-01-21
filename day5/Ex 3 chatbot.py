# day5/chatbot.py
"""
Exercise 5.3:Simple customer support chatbot
This is what we'll EVALUATE using our golden dataset
"""

import os
from openai import OpenAI

# Set your API key
os.environ['OPENAI_API_KEY'] = ''

client = OpenAI()

class CustomerSupportBot:
    """
    Basic customer support chatbot for a SaaS product
    """
    
    def __init__(self):
        self.system_prompt = """You are a customer support agent for a SaaS product.

RESPONSE FORMAT:
1. Acknowledge the customer's situation with empathy (1 sentence)
2. Provide accurate, specific answer to their question (2-3 sentences)
3. Offer next steps or escalation if needed (1 sentence)

EMPATHY (Show understanding):
- Start with: "I understand...", "I'm sorry to hear...", "That must be frustrating..."
- Validate feelings: "You're right to be concerned", "That's completely understandable"
- Use warm tone throughout

ACCURACY (Be precise and helpful):
- Answer the specific question asked
- Provide concrete steps or information
- If you don't know: Say so clearly, then escalate
- For billing: Explain policies, refund timelines, next steps
- For technical: Provide troubleshooting steps, documentation links
- For how-to: Give step-by-step instructions

ESCALATION (When to involve humans):
- Legal threats ("sue", "lawyer", "legal") → Escalate to legal team immediately
- Very angry customers (caps, strong language, multiple complaints) → Escalate to supervisor
- Questions requiring account access or data you can't see → Escalate to support team
- Complex technical issues beyond basic troubleshooting → Escalate to technical team

EXAMPLES:

Bad (too empathetic, vague):
"I'm so sorry you're experiencing this terrible issue! That must be incredibly frustrating for you. Let me see what I can do to help make this better for you!"

Bad (accurate but cold):
"Your subscription can be cancelled in Settings > Billing > Cancel. Data is retained for 30 days."

Good (balanced):
"I understand how frustrating billing issues can be. To cancel your subscription, go to Settings > Billing > Cancel Subscription. Your data will be retained for 30 days in case you want to reactivate. Is there anything I can help resolve before you cancel?"

Keep responses concise (2-4 sentences) but complete."""
    def get_response(self, user_input: str, context: dict = None) -> str:
        """
        Generate chatbot response
        
        Args:
            user_input: Customer's question
            context: Background info about user
        
        Returns:
            Chatbot's response
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context if provided
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            messages.append({
                "role": "system", 
                "content": f"User context:\n{context_str}"
            })
        
        # Add user's question
        messages.append({"role": "user", "content": user_input})
        
        # Get response from GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content

# Test it
if __name__ == "__main__":
    bot = CustomerSupportBot()
    
    print("Testing Customer Support Bot")
    print("=" * 60)
    
    # Test 1: Billing question
    print("\nTest 1: Billing")
    response = bot.get_response(
        "I was charged twice this month",
        context={"user_tier": "premium", "account_status": "active"}
    )
    print(f"Customer: I was charged twice this month")
    print(f"Bot: {response}")
    
    # Test 2: Angry customer
    print("\n" + "=" * 60)
    print("\nTest 2: Escalation")
    response = bot.get_response(
        "This is ridiculous! I've been waiting for days!",
        context={"previous_bot_interactions": 5}
    )
    print(f"Customer: This is ridiculous! I've been waiting for days!")
    print(f"Bot: {response}")
