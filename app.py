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
            <p>Built with OpenAI model="gpt-3.5-turbo",. Synthetic research for rapid validation.</p>
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
            {"name": "Marco Rossi", "age": 38, "occupation": "Professional Chef", "traits": "Perfectionist, values technique, skeptical of shortcuts, judges apps by recipe authenticity, high culinary standards"},
            {"name": "Jennifer Walsh", "age": 34, "occupation": "Working Mother of Two", "traits": "Time-starved, needs family-friendly meals, values convenience but wants healthy options, budget-conscious for groceries"},
            {"name": "David Chen", "age": 28, "occupation": "Food Blogger & Content Creator", "traits": "Trend-focused, loves experimenting with new cuisines, visual presentation matters, shares everything on social media, needs Instagram-worthy results"}
        ]
    elif any(word in product_lower for word in ['fitness', 'workout', 'gym', 'health', 'exercise', 'training', 'yoga', 'running']):
        return [
            {"name": "Alex Rivera", "age": 29, "occupation": "Personal Trainer & Nutrition Coach", "traits": "Data-obsessed, needs measurable results, skeptical of fitness fads, science-based approach, wants client progress tracking"},
            {"name": "Sarah Mitchell", "age": 42, "occupation": "Corporate Executive", "traits": "Time-poor, stress management focus, willing to pay for convenience, needs flexibility for travel schedule, beginner-friendly workouts"},
            {"name": "Jordan Park", "age": 24, "occupation": "College Student & Part-time Barista", "traits": "Budget-conscious, social motivation from friends, beginner-friendly needs, influenced by fitness influencers on TikTok, wants quick dorm-room workouts"}
        ]
    elif any(word in product_lower for word in ['finance', 'money', 'budget', 'invest', 'stock', 'crypto', 'trading', 'saving']):
        return [
            {"name": "Robert Chen", "age": 45, "occupation": "Certified Financial Planner", "traits": "Risk-averse with client money, needs regulatory compliance, skeptical of robo-advisors, values personal relationships over algorithms"},
            {"name": "Emily Rodriguez", "age": 31, "occupation": "Tech Startup Employee", "traits": "High disposable income, wants automated investing, interested in crypto, values time over micromanagement, willing to pay for premium features"},
            {"name": "Michael Thompson", "age": 58, "occupation": "High School Principal", "traits": "Conservative approach, nearing retirement, needs simplicity, distrusts new fintech, wants guaranteed returns over speculation, needs educational resources"}
        ]
    elif any(word in product_lower for word in ['education', 'learn', 'course', 'student', 'study', 'school', 'teaching', 'tutor']):
        return [
            {"name": "Dr. Amanda Foster", "age": 52, "occupation": "University Professor", "traits": "Academic rigor, skeptical of ed-tech trends, values accreditation, needs administrative tools, wants measurable learning outcomes for students"},
            {"name": "Tyler Johnson", "age": 20, "occupation": "Computer Science Student", "traits": "Self-taught learner, prefers video content, wants industry-relevant skills, price-sensitive as a student, values community and peer feedback"},
            {"name": "Lisa Park", "age": 36, "occupation": "Homeschooling Parent", "traits": "Curriculum control is crucial, needs progress tracking for multiple children, values safety and age-appropriate content, willing to invest in quality education tools"}
        ]
    elif any(word in product_lower for word in ['travel', 'trip', 'vacation', 'hotel', 'flight', 'booking', 'destination']):
        return [
            {"name": "James Morrison", "age": 41, "occupation": "Management Consultant", "traits": "Frequent business traveler, loyalty program obsessed, needs seamless booking, values time over money, wants automatic itinerary management"},
            {"name": "Sofia Patel", "age": 27, "occupation": "Remote Software Developer", "traits": "Digital nomad lifestyle, budget backpacker turned comfortable traveler, values authentic local experiences, plans trips around coworking spaces"},
            {"name": "The Williams Family", "age": 45, "occupation": "Parents of Three", "traits": "Safety-first for kids, needs all-inclusive convenience, plans around school schedules, values memories over luxury, overwhelmed by planning logistics"}
        ]
    elif any(word in product_lower for word in ['shopping', 'ecommerce', 'buy', 'store', 'retail', 'fashion', 'clothes']):
        return [
            {"name": "Victoria Chang", "age": 33, "occupation": "Fashion Buyer for Department Store", "traits": "Trend forecaster, quality over quantity, skeptical of fast fashion, wants exclusive access, values sustainability credentials, early adopter of new brands"},
            {"name": "Marcus Johnson", "age": 29, "occupation": "Warehouse Supervisor", "traits": "Deal hunter, compares prices across multiple sites, reads reviews religiously, budget-conscious but splurges on hobbies, wants fast shipping"},
            {"name": "Betty Thompson", "age": 68, "occupation": "Retired Nurse", "traits": "Needs simplicity, distrusts online payments, wants phone support available, values familiar brands, frustrated by complicated return processes, shops for grandchildren"}
        ]
    else:
        return [
            {"name": "Alex Thompson", "age": 32, "occupation": "Product Manager at Tech Company", "traits": "Analytical decision-maker, skeptical of marketing claims, needs data-driven proof, compares multiple alternatives before committing, values integration with existing tools"},
            {"name": "Jordan Lee", "age": 28, "occupation": "Marketing Specialist", "traits": "Early adopter of new tools, enthusiastic about innovation, values convenience and user experience over price, influenced by peer recommendations, willing to pay premium for time savings"},
            {"name": "Casey Martinez", "age": 35, "occupation": "Operations Director", "traits": "Risk-averse, budget-conscious with clear ROI requirements, needs simplicity and minimal training, worried about team adoption, prefers proven solutions over bleeding edge"}
        ]

@app.route('/')
def home():
    """Render the main page"""
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route('/generate-personas', methods=['POST'])
def generate_personas():
    """Generate personas using OpenAI or fallback"""
    try:
        data = request.get_json()
        product_description = data.get('product_description', '')
        target_market = data.get('target_market', '')
        
        if not product_description:
            return jsonify({"error": "No product description provided"}), 400
        
        # Try OpenAI first
        try:
            prompt = f"""Analyze this product and create 3 realistic user personas who would actually use it.

Product: "{product_description}"
Target: {target_market or 'General consumers'}

Create personas that are SPECIFIC to this product type. Consider:
- What jobs/roles would actually use this?
- What ages make sense for this product?
- What personality traits relate to HOW they'd use it?

Make them DISTINCT:
- One expert/skeptical type who demands proof
- One enthusiastic early adopter who sees potential
- One practical user who needs clear value

Return valid JSON only:
[
  {{"name": "Full Name", "age": 32, "occupation": "Job Title", "traits": "3-4 specific traits"}},
  {{"name": "Full Name", "age": 28, "occupation": "Job Title", "traits": "3-4 specific traits"}},
  {{"name": "Full Name", "age": 35, "occupation": "Job Title", "traits": "3-4 specific traits"}}
]"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            personas = json.loads(content.strip())
            
            # Validate structure
            if len(personas) == 3 and all('name' in p and 'age' in p and 'occupation' in p and 'traits' in p for p in personas):
                return jsonify({"personas": personas})
            else:
                # Fall back to contextual if validation fails
                personas = get_contextual_personas(product_description)
                return jsonify({"personas": personas})
                
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fall back to contextual personas
            personas = get_contextual_personas(product_description)
            return jsonify({"personas": personas})
        
    except Exception as e:
        print(f"Error in generate_personas: {e}")
        return jsonify({"error": "Failed to generate personas"}), 500

@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    """Run the focus group simulation"""
    try:
        # Get product description
        product_description = request.form.get('product_description', 'New product')
        
        # Collect persona data from form
        personas_data = []
        for i in range(1, 4):
            persona = {
                'name': request.form.get(f'name{i}', f'Person {i}'),
                'age': int(request.form.get(f'age{i}', 30)),
                'occupation': request.form.get(f'job{i}', 'Professional'),
                'traits': request.form.get(f'traits{i}', 'Average user')
            }
            personas_data.append(persona)
        
        # Generate responses based on persona traits
        responses = []
        
        for p in personas_data:
            traits_lower = p['traits'].lower()
            
            # Determine role and response based on traits
            if any(word in traits_lower for word in ['skeptic', 'analytical', 'data', 'perfectionist', 'scientific', 'rigid']):
                role = "The Expert/Skeptic"
                text = f"As a {p['occupation']}, I approach this with professional skepticism. Being {p['traits'].split(',')[0].lower()}, I've seen too many products overpromise and underdeliver. I need to see third-party validation, user reviews, and ideally a free trial period to evaluate whether this actually works as claimed. My main concern is reliability - if I commit to this, it needs to work flawlessly. I'd also want to know about data privacy and what happens if I want to cancel. The concept has merit, but I'm not convinced yet."
                
            elif any(word in traits_lower for word in ['enthusiast', 'early adopter', 'optimistic', 'trend', 'experimental', 'influencer']):
                role = "The Early Adopter"
                text = f"I'm genuinely excited about this! As someone who's {p['traits'].split(',')[0].lower()}, I can see the potential immediately. This addresses a real pain point I've experienced personally. I'd definitely try it out - the value proposition is clear to me, and I'm willing to be among the first users. My main question is about the roadmap - what features are coming next? I want to know I'm investing in a product that will keep improving. I'm also likely to share this with my network if it delivers."
                
            else:
                role = "The Practical User"
                text = f"I'm interested but need to be practical about this decision. As a {p['occupation']}, {p['traits'].split(',')[0].lower()}, so I need to carefully evaluate whether this justifies the cost and time investment. I'd start with whatever free option is available, but I'd need to see clear value within the first week to continue. My biggest concern is adoption - will I actually use this consistently, or will it become another forgotten subscription? I also worry about customer support if something goes wrong. Show me how this makes my life easier, and I'm in."
            
            responses.append({
                'name': p['name'],
                'role': role,
                'text': text
            })
        
        # Generate contextual insight based on product type
        product_lower = product_description.lower()
        
        if any(word in product_lower for word in ['recipe', 'cook', 'food']):
            insight = "Your expert persona (chef) needs authenticity - emphasize recipe testing and professional credibility. Your busy parent needs convenience without sacrificing nutrition - highlight meal planning and grocery list features. Your content creator needs visual appeal - focus on presentation and social features. Price sensitivity varies: professionals pay for quality, families watch budgets, creators want growth tools."
        elif any(word in product_lower for word in ['fitness', 'workout', 'gym']):
            insight = "The trainer needs data and progress tracking features. The executive needs time efficiency and flexibility - emphasize quick workouts and travel-friendly options. The student needs affordability and social motivation - consider a free tier and community features. All segments care about results, but measure them differently: professionals want performance data, executives want stress relief, students want visible changes."
        elif any(word in product_lower for word in ['finance', 'money', 'invest']):
            insight = "The financial planner needs compliance and security assurances - emphasize regulation and data protection. The tech worker wants automation and modern features - highlight AI and mobile experience. The near-retiree needs stability and education - focus on guaranteed returns and learning resources. Trust is the key barrier: professionals need credentials, tech workers want innovation, retirees want safety."
        else:
            insight = "Your skeptical persona needs social proof - add testimonials, case studies, and metrics. Your enthusiast is your ideal early adopter - target them for beta programs and referrals. Your practical user represents your retention risk - focus on onboarding simplicity and quick wins. Consider tiered pricing: premium for enthusiasts, standard for skeptics (once convinced), and basic for practical users testing the waters."
        
        result = {
            'product': product_description[:100] + '...' if len(product_description) > 100 else product_description,
            'responses': responses,
            'insight': insight
        }
        
        return render_template_string(HTML_TEMPLATE, result=result)
        
    except Exception as e:
        print(f"Error in run_simulation: {e}")
        return render_template_string(HTML_TEMPLATE, result={
            'product': "Error running simulation",
            'responses': [
                {'name': 'System', 'role': 'Error', 'text': f'An error occurred: {str(e)}. Please try again.'}
            ],
            'insight': 'Make sure all persona fields are filled out correctly.'
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "api_key_configured": bool(api_key)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("🚀 FocusGroupAI Starting...")
    print("=" * 60)
    print(f"✅ OpenAI API Key: {'Configured' if api_key else 'Not configured'}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)


