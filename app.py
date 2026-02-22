import os
import json
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI

# Initialize Flask
app = Flask(__name__)

# Get API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it before running the app.")

os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI(api_key=api_key)

# Complete HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusGroupAI — AI-Powered User Research</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0f;
            color: #ffffff;
            line-height: 1.6;
            min-height: 100vh;
        }
        .gradient-bg {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(255, 119, 198, 0.15) 0%, transparent 50%);
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 8px 16px;
            border-radius: 100px;
            font-size: 13px;
            font-weight: 500;
            color: #818cf8;
            margin-bottom: 20px;
        }
        .badge::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        h1 {
            font-size: 56px;
            font-weight: 700;
            margin-bottom: 16px;
            background: linear-gradient(180deg, #fff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }
        .subtitle {
            color: #64748b;
            font-size: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 32px;
            margin-bottom: 24px;
            backdrop-filter: blur(10px);
        }
        .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #818cf8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #cbd5e1;
            margin-bottom: 8px;
        }
        input, textarea, select {
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 14px 16px;
            color: #fff;
            font-size: 15px;
            font-family: inherit;
            transition: all 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: rgba(99, 102, 241, 0.5);
            background: rgba(255, 255, 255, 0.08);
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        .btn {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            margin-left: 12px;
            box-shadow: none;
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        .btn-full {
            width: 100%;
            padding: 18px;
            font-size: 18px;
        }
        .persona-form {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        .persona-form:hover {
            border-color: rgba(255, 255, 255, 0.1);
        }
        .persona-form h3 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        .generated-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .response-box {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin-top: 20px;
            border-left: 4px solid #6366f1;
        }
        .message-author {
            font-size: 14px;
            font-weight: 600;
            color: #818cf8;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .message-author::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #818cf8;
            border-radius: 50%;
        }
        .message-text {
            font-size: 15px;
            color: #cbd5e1;
            line-height: 1.7;
        }
        .insight-box {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.05) 100%);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 16px;
            padding: 28px;
            margin-top: 28px;
        }
        .insight-title {
            font-size: 13px;
            font-weight: 700;
            color: #22c55e;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .insight-title::before {
            content: '→';
            font-size: 16px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #64748b;
        }
        .spinner {
            width: 48px;
            height: 48px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .features {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            text-align: center;
            padding: 24px;
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .feature-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        .feature h4 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .feature p {
            font-size: 14px;
            color: #64748b;
        }
        .pricing {
            text-align: center;
            margin: 40px 0;
        }
        .price {
            font-size: 64px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .price-period {
            color: #64748b;
            font-size: 18px;
        }
        footer {
            text-align: center;
            padding: 40px;
            color: #64748b;
            font-size: 14px;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 60px;
        }
        @media (max-width: 768px) {
            h1 { font-size: 40px; }
            .features { grid-template-columns: 1fr; }
            .grid-2 { grid-template-columns: 1fr; }
            .btn-secondary { margin-left: 0; margin-top: 12px; display: block; width: 100%; }
        }
    </style>
</head>
<body>
    <div class="gradient-bg"></div>
    <div class="container">
        <div class="header">
            <div class="badge">Now Live — Generate personas in seconds</div>
            <h1>FocusGroupAI</h1>
            <p class="subtitle">AI-powered user research. Create realistic personas and get instant feedback on your product ideas.</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h4>Instant Personas</h4>
                <p>AI generates 3 distinct user profiles from your product description</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🎯</div>
                <h4>Realistic Feedback</h4>
                <p>Get authentic responses based on persona traits and behaviors</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💡</div>
                <h4>Actionable Insights</h4>
                <p>Receive strategic recommendations for your go-to-market</p>
            </div>
        </div>
        
        <form id="mainForm" method="POST" action="/run-simulation">
            <!-- STEP 1: Product Description -->
            <div class="card">
                <div class="section-title">Step 1: Describe Your Product</div>
                <div class="form-group">
                    <label>What are you building?</label>
                    <textarea name="product_description" id="productDesc" placeholder="Example: An AI fitness app that creates personalized 15-minute home workouts based on your schedule and available equipment. $12.99/month with 7-day free trial." required></textarea>
                </div>
                <div class="form-group">
                    <label>Target Market (optional)</label>
                    <input type="text" name="target_market" id="targetMarket" placeholder="Example: Busy professionals aged 25-40 who struggle to find time for the gym">
                </div>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    <button type="button" class="btn" onclick="generatePersonas()">
                        ✨ Auto-Generate Personas
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="fillExample()">
                        Try Example
                    </button>
                </div>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing your product and creating realistic personas...</p>
                </div>
            </div>

            <!-- STEP 2: Personas -->
            <div class="card" id="personasCard">
                <div class="section-title">Step 2: Your Focus Group Participants</div>
                <p style="color: #64748b; margin-bottom: 24px;">Review and edit these AI-generated personas, or create your own.</p>
                
                <!-- Persona 1 -->
                <div class="persona-form">
                    <h3>Persona 1 <span class="generated-badge" id="badge1" style="display:none;">AI Generated</span></h3>
                    <div class="grid-2">
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name1" id="name1" placeholder="e.g., Marcus Chen" required>
                        </div>
                        <div class="form-group">
                            <label>Age</label>
                            <input type="number" name="age1" id="age1" placeholder="32" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Occupation</label>
                        <input type="text" name="job1" id="job1" placeholder="e.g., Software Engineer" required>
                    </div>
                    <div class="form-group">
                        <label>Personality & Traits</label>
                        <input type="text" name="traits1" id="traits1" placeholder="e.g., Analytical, data-driven, skeptical of marketing claims" required>
                    </div>
                </div>

                <!-- Persona 2 -->
                <div class="persona-form">
                    <h3>Persona 2 <span class="generated-badge" id="badge2" style="display:none;">AI Generated</span></h3>
                    <div class="grid-2">
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name2" id="name2" placeholder="e.g., Sarah Williams" required>
                        </div>
                        <div class="form-group">
                            <label>Age</label>
                            <input type="number" name="age2" id="age2" placeholder="28" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Occupation</label>
                        <input type="text" name="job2" id="job2" placeholder="e.g., Marketing Director" required>
                    </div>
                    <div class="form-group">
                        <label>Personality & Traits</label>
                        <input type="text" name="traits2" id="traits2" placeholder="e.g., Early adopter, enthusiastic, values convenience" required>
                    </div>
                </div>

                <!-- Persona 3 -->
                <div class="persona-form">
                    <h3>Persona 3 <span class="generated-badge" id="badge3" style="display:none;">AI Generated</span></h3>
                    <div class="grid-2">
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name3" id="name3" placeholder="e.g., Lisa Rodriguez" required>
                        </div>
                        <div class="form-group">
                            <label>Age</label>
                            <input type="number" name="age3" id="age3" placeholder="35" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Occupation</label>
                        <input type="text" name="job3" id="job3" placeholder="e.g., Elementary School Teacher" required>
                    </div>
                    <div class="form-group">
                        <label>Personality & Traits</label>
                        <input type="text" name="traits3" id="traits3" placeholder="e.g., Budget-conscious, needs simplicity, risk-averse" required>
                    </div>
                </div>
            </div>

            <!-- STEP 3: Run Simulation -->
            <div class="card">
                <div class="section-title">Step 3: Run Your AI Focus Group</div>
                <button type="submit" class="btn btn-full">
                    🚀 Generate Focus Group Insights
                </button>
                <p style="text-align: center; color: #64748b; margin-top: 16px; font-size: 14px;">
                    Takes 10-15 seconds • No credit card required
                </p>
            </div>
        </form>

        {% if result %}
        <div class="card">
            <div class="section-title">Focus Group Results</div>
            <p style="color: #64748b; margin-bottom: 24px; font-size: 15px;">Product tested: {{ result.product }}</p>
            
            {% for response in result.responses %}
            <div class="response-box">
                <div class="message-author">{{ response.name }} — {{ response.role }}</div>
                <div class="message-text">{{ response.text }}</div>
            </div>
            {% endfor %}
            
            <div class="insight-box">
                <div class="insight-title">Strategic Recommendation</div>
                <div style="color: #e2e8f0; font-size: 15px; line-height: 1.8;">
                    {{ result.insight }}
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 32px;">
                <a href="/" class="btn" style="text-decoration: none;">Run Another Focus Group</a>
            </div>
        </div>
        {% endif %}
        
        <div class="pricing">
            <div class="price">$49<span style="font-size: 24px; color: #64748b;">/mo</span></div>
            <div class="price-period">Unlimited focus groups • Cancel anytime</div>
        </div>
        
        <footer>
            <p>Built with OpenAI GPT-4. Synthetic research for rapid validation.</p>
            <p style="margin-top: 8px;">© 2025 FocusGroupAI. All rights reserved.</p>
        </footer>
    </div>

    <script>
        async function generatePersonas() {
            const productDesc = document.getElementById('productDesc').value;
            const targetMarket = document.getElementById('targetMarket').value;
            
            if (!productDesc) {
                alert('Please describe your product first');
                document.getElementById('productDesc').focus();
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            
            try {
                const response = await fetch('/generate-personas', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        product_description: productDesc,
                        target_market: targetMarket
                    })
                });
                
                const data = await response.json();
                
                if (data.personas && data.personas.length === 3) {
                    for (let i = 0; i < 3; i++) {
                        const p = data.personas[i];
                        document.getElementById('name' + (i+1)).value = p.name || '';
                        document.getElementById('age' + (i+1)).value = p.age || '';
                        document.getElementById('job' + (i+1)).value = p.occupation || '';
                        document.getElementById('traits' + (i+1)).value = p.traits || '';
                        document.getElementById('badge' + (i+1)).style.display = 'inline-flex';
                    }
                    
                    document.getElementById('personasCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    alert('Error generating personas. Please try again or enter manually.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error. Please check your internet and try again.');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function fillExample() {
            document.getElementById('productDesc').value = "An AI recipe app that suggests meals based on ingredients you already have in your kitchen. Reduces food waste and saves money. $9.99/month with a 14-day free trial. Includes meal planning and grocery list features.";
            document.getElementById('targetMarket').value = "Home cooks aged 25-45 who want to reduce food waste and save time on meal planning";
            
            document.getElementById('name1').value = "Marco Rossi";
            document.getElementById('age1').value = "38";
            document.getElementById('job1').value = "Professional Chef";
            document.getElementById('traits1').value = "Perfectionist, values technique, skeptical of shortcuts, judges apps by recipe authenticity";
            
            document.getElementById('name2').value = "Jennifer Walsh";
            document.getElementById('age2').value = "34";
            document.getElementById('job2').value = "Working Mother of Two";
            document.getElementById('traits2').value = "Time-starved, needs family-friendly meals, values convenience but wants healthy options";
            
            document.getElementById('name3').value = "David Chen";
            document.getElementById('age3').value = "28";
            document.getElementById('job3').value = "Food Blogger";
            document.getElementById('traits3').value = "Trend-focused, loves experimenting, visual presentation matters, shares on social media";
            
            document.getElementById('badge1').style.display = 'inline-flex';
            document.getElementById('badge2').style.display = 'inline-flex';
            document.getElementById('badge3').style.display = 'inline-flex';
        }
    </script>
</body>
</html>
"""

def get_contextual_personas(product_description):
    """Generate contextual fallback personas based on product type"""
    product_lower = product_description.lower()
    
    if any(word in product_lower for word in ['recipe', 'cook', 'food', 'meal', 'kitchen', 'chef', 'baking', 'ingredient']):
        return [
            {"name": "Marco Rossi", "age": 38, "occupation": "Professional Chef", "traits": "Perfectionist, values technique, skeptical of shortcuts, judges apps by recipe authenticity"},
            {"name": "Jennifer Walsh", "age": 34, "occupation": "Working Mother of Two", "traits": "Time-starved, needs family-friendly meals, values convenience but wants healthy options"},
            {"name": "David Chen", "age": 28, "occupation": "Food Blogger", "traits": "Trend-focused, loves experimenting, visual presentation matters, shares on social media"}
        ]
    elif any(word in product_lower for word in ['fitness', 'workout', 'exercise', 'gym', 'health', 'wellness', 'yoga']):
        return [
            {"name": "Alex Thompson", "age": 32, "occupation": "Software Engineer", "traits": "Analytical, data-driven, wants measurable results, skeptical of fitness fads"},
            {"name": "Maya Patel", "age": 28, "occupation": "Yoga Instructor", "traits": "Holistic approach, values mind-body connection, prefers low-impact workouts"},
            {"name": "James Wilson", "age": 45, "occupation": "Busy Executive", "traits": "Time-poor, needs efficiency, willing to pay for convenience, likes quick results"}
        ]
    elif any(word in product_lower for word in ['finance', 'banking', 'invest', 'money', 'budget', 'saving']):
        return [
            {"name": "Sarah Chen", "age": 35, "occupation": "Financial Analyst", "traits": "Risk-averse, detail-oriented, wants security and transparency"},
            {"name": "Marcus Webb", "age": 24, "occupation": "Recent Graduate", "traits": "New to investing, wants education, needs simple interface, budget-conscious"},
            {"name": "Linda Martinez", "age": 52, "occupation": "Small Business Owner", "traits": "Practical, values time-saving tools, wants to separate business/personal finances"}
        ]
    else:
        return [
            {"name": "Marcus Chen", "age": 32, "occupation": "Software Engineer", "traits": "Analytical, data-driven, skeptical of marketing claims, values efficiency"},
            {"name": "Sarah Williams", "age": 28, "occupation": "Marketing Director", "traits": "Early adopter, enthusiastic, values convenience and design"},
            {"name": "Lisa Rodriguez", "age": 35, "occupation": "Elementary School Teacher", "traits": "Budget-conscious, needs simplicity, risk-averse, values community"}
        ]

@app.route('/')
def index():
    """Render the main page"""
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route('/generate-personas', methods=['POST'])
def generate_personas():
    """Generate personas using OpenAI"""
    try:
        data = request.json
        product_description = data.get('product_description', '')
        target_market = data.get('target_market', '')
        
        # Check for API key and try to use OpenAI
        if api_key and api_key != "your-openai-api-key-here":
            try:
                prompt = f"""Based on this product description, generate 3 detailed user personas for a focus group.
                
Product Description: {product_description}
Target Market: {target_market if target_market else 'General consumers'}

For each persona, provide:
1. Name (realistic and diverse)
2. Age (specific number)
3. Occupation
4. Personality & Traits (comma-separated, descriptive)

Format your response as a JSON array with objects containing keys: name, age, occupation, traits
Make the personas diverse in age, background, and perspective. Each should have a unique viewpoint on this product."""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a user research expert who creates realistic personas. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=800
                )
                
                # Parse the response
                personas_text = response.choices[0].message.content.strip()
                # Clean up the response to ensure it's valid JSON
                if personas_text.startswith('```json'):
                    personas_text = personas_text[7:]
                if personas_text.startswith('```'):
                    personas_text = personas_text[3:]
                if personas_text.endswith('```'):
                    personas_text = personas_text[:-3]
                
                personas = json.loads(personas_text)
                return jsonify({"personas": personas})
                
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall back to contextual personas
                personas = get_contextual_personas(product_description)
                return jsonify({"personas": personas})
        else:
            # No valid API key, use contextual personas
            personas = get_contextual_personas(product_description)
            return jsonify({"personas": personas})
            
    except Exception as e:
        print(f"Error in generate_personas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    """Run the focus group simulation"""
    try:
        # Get form data
        product_description = request.form.get('product_description', '')
        
        # Collect persona data
        personas = []
        for i in range(1, 4):
            persona = {
                "name": request.form.get(f'name{i}', ''),
                "age": request.form.get(f'age{i}', ''),
                "occupation": request.form.get(f'job{i}', ''),
                "traits": request.form.get(f'traits{i}', '')
            }
            personas.append(persona)
        
        # Generate focus group responses
        responses = []
        
        if api_key and api_key != "your-openai-api-key-here":
            try:
                # Create a prompt for each persona
                for persona in personas:
                    prompt = f"""You are participating in a focus group for a new product. Respond as this specific persona:

Persona: {persona['name']}, Age {persona['age']}, {persona['occupation']}
Traits: {persona['traits']}

Product: {product_description}

Provide a realistic, detailed response (2-3 sentences) about:
1. Your initial reaction to this product
2. Would you use it? Why or why not?
3. What concerns or questions do you have?

Stay completely in character based on the persona traits."""

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a realistic focus group participant. Respond in character with authentic, detailed feedback."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.9,
                        max_tokens=200
                    )
                    
                    responses.append({
                        "name": persona['name'],
                        "role": f"{persona['age']} • {persona['occupation']}",
                        "text": response.choices[0].message.content.strip()
                    })
                
                # Generate strategic insight
                insight_prompt = f"""Based on these focus group responses, provide a strategic recommendation:

Product: {product_description}

Participant 1 ({personas[0]['name']} - {personas[0]['traits']}): {responses[0]['text'] if len(responses) > 0 else ''}

Participant 2 ({personas[1]['name']} - {personas[1]['traits']}): {responses[1]['text'] if len(responses) > 1 else ''}

Participant 3 ({personas[2]['name']} - {personas[2]['traits']}): {responses[2]['text'] if len(responses) > 2 else ''}

Provide a concise strategic recommendation (3-4 sentences) for the product team. Focus on:
1. Key themes from the feedback
2. Suggested improvements
3. Go-to-market considerations"""

                insight_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a product strategy consultant. Provide actionable, data-driven recommendations."},
                        {"role": "user", "content": insight_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                insight = insight_response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"OpenAI API error in simulation: {e}")
                # Fall back to mock responses
                responses, insight = generate_mock_responses(product_description, personas)
        else:
            # No API key, use mock responses
            responses, insight = generate_mock_responses(product_description, personas)
        
        result = {
            "product": product_description[:100] + "..." if len(product_description) > 100 else product_description,
            "responses": responses,
            "insight": insight
        }
        
        return render_template_string(HTML_TEMPLATE, result=result)
        
    except Exception as e:
        print(f"Error in run_simulation: {e}")
        return render_template_string(HTML_TEMPLATE, result={
            "product": "Error running simulation",
            "responses": [
                {"name": "System", "role": "Error", "text": f"An error occurred: {str(e)}"}
            ],
            "insight": "Please try again. Make sure all persona fields are filled out correctly."
        })

def generate_mock_responses(product_description, personas):
    """Generate mock responses when OpenAI is not available"""
    responses = []
    
    # Mock responses based on persona traits
    for persona in personas:
        traits_lower = persona['traits'].lower()
        
        if 'skeptical' in traits_lower or 'analytical' in traits_lower:
            text = f"As someone who's skeptical of new products, I'd need to see some solid data before committing. The concept sounds interesting, but I'm concerned about how well it actually works in practice. I'd probably wait for reviews from trusted sources before trying it."
        elif 'early adopter' in traits_lower or 'enthusiastic' in traits_lower:
            text = f"This sounds amazing! I love trying new products and this seems right up my alley. The convenience factor is huge for me. I'd sign up for the free trial immediately and probably become a power user if it delivers on its promises."
        elif 'budget-conscious' in traits_lower or 'risk-averse' in traits_lower:
            text = f"I like the idea, but I'm worried about the monthly cost. $9.99 adds up over time. I'd need to be really sure it would save me money before committing. The free trial would be essential for me to test if it's worth the investment."
        elif 'time-starved' in traits_lower or 'busy' in traits_lower:
            text = f"Time is my biggest constraint, so if this actually saves me time, I'm interested. But I don't have bandwidth to learn complicated systems. It needs to be intuitive and work right out of the box. The convenience factor would determine whether I stick with it."
        else:
            text = f"This product addresses a real need I have. I like the concept and would definitely give it a try. My main question is about how well it adapts to individual preferences and whether the recommendations actually get better over time with more data."
        
        responses.append({
            "name": persona['name'],
            "role": f"{persona['age']} • {persona['occupation']}",
            "text": text
        })
    
    # Generate mock insight
    insight = "Based on the focus group feedback, there's genuine interest in the product concept, but concerns about pricing and ease of use are consistent across personas. Consider emphasizing the free trial period in marketing to reduce adoption friction. The convenience factor is a strong selling point, but you'll need to provide concrete evidence of value to convert skeptical users. Early adopter feedback suggests potential for strong word-of-mouth if the experience exceeds expectations."
    
    return responses, insight

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "api_key_configured": bool(api_key and api_key != "your-openai-api-key-here")})

if __name__ == '__main__':
    print("🚀 FocusGroupAI Starting...")
    print(f"✅ OpenAI API Key: {'Configured' if api_key and api_key != 'your-openai-api-key-here' else 'Not configured - using fallback responses'}")
    print("🌐 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)