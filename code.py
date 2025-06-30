import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="💰 Mon Budget Épique",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration des couleurs et style
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'gradient': 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)'
}

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .budget-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .expense-form {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e3e8ff;
    }
    .success-alert {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-alert {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .danger-alert {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .treasure-chest {
        background: url('https://cdn.pixabay.com/photo/2016/04/01/10/59/treasure-1299587_1280.png');
        background-size: cover;
        padding: 2rem;
        border-radius: 15px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

class BudgetManager:
    def __init__(self):
        self.data_file = "budget_data.json"
        self.users_file = "users.json"
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except:
            self.data = {}
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except:
            self.users = {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = self.hash_password(password)
        self.data[username] = {
            'months': {},
            'savings': 0,
            'achievements': {},
            'avatar': 'Chevalier',
            'points': 0,
            'theme': 'Clair'
        }
        self.save_data()
        return True
    
    def authenticate(self, username, password):
        if username not in self.users:
            return False
        return self.users[username] == self.hash_password(password)
    
    def get_user_data(self, username):
        default_data = {
            'months': {},
            'savings': 0,
            'achievements': {},
            'avatar': 'Chevalier',
            'points': 0,
            'theme': 'Clair'
        }
        user_data = self.data.get(username, default_data)
        # Ensure all required fields are present
        for key, value in default_data.items():
            if key not in user_data:
                user_data[key] = value
        self.data[username] = user_data
        self.save_data()
        return user_data
    
    def update_user_data(self, username, data):
        self.data[username] = data
        self.save_data()

def login_page():
    st.markdown('<div class="main-header"><h1>💰 Mon Budget Épique</h1><p>Devenez le héros de vos finances !</p></div>', unsafe_allow_html=True)
    
    # Afficher une image statique
    st.image("https://cdn.pixabay.com/photo/2016/04/01/10/59/treasure-1299587_1280.png", width=200)
    
    tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
    
    with tab1:
        st.markdown("### Connectez-vous à votre aventure financière")
        username = st.text_input("👤 Nom d'utilisateur", key="login_user")
        password = st.text_input("🔒 Mot de passe", type="password", key="login_pass")
        
        if st.button("Se connecter", use_container_width=True):
            if budget_manager.authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Bienvenue, héros financier !")
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
    
    with tab2:
        st.markdown("### Commencez votre quête financière")
        new_username = st.text_input("👤 Nom d'utilisateur", key="reg_user")
        new_password = st.text_input("🔒 Mot de passe", type="password", key="reg_pass")
        confirm_password = st.text_input("🔒 Confirmer le mot de passe", type="password", key="reg_confirm")
        
        if st.button("S'inscrire", use_container_width=True):
            if new_password != confirm_password:
                st.error("❌ Les mots de passe ne correspondent pas")
            elif len(new_password) < 4:
                st.error("❌ Le mot de passe doit contenir au moins 4 caractères")
            elif budget_manager.register_user(new_username, new_password):
                st.success("✅ Compte créé ! Entrez dans la légende !")
            else:
                st.error("❌ Ce nom d'utilisateur existe déjà")

def sidebar_navigation():
    user_data = budget_manager.get_user_data(st.session_state.username)
    st.sidebar.markdown(f"### 👋 {user_data['avatar']} {st.session_state.username}")
    st.sidebar.markdown(f"🌟 Pièces d'Or: {user_data['points']}")
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Tableau de bord": "dashboard",
        "📋 Planification mensuelle": "planning",
        "💸 Ajouter une dépense": "add_expense",
        "💰 Gérer les entrées": "manage_income",
        "📈 Suivi du mois": "monthly_tracking",
        "📚 Historique": "history",
        "⚔️ Quêtes": "quests",
        "🧙‍♂️ Conseiller Financier": "advisor",
        "🏫 Académie Financière": "academy",
        "⚙️ Paramètres": "settings"
    }
    
    selected = st.sidebar.radio("Navigation", list(pages.keys()))
    return pages[selected]

def get_current_month_key():
    return datetime.now().strftime("%Y-%m")

def get_categories():
    return ["Transport", "Nourriture", "Factures", "Santé", "Divers"]

def update_achievements(username, user_data):
    achievements = user_data.get('achievements', {})
    savings = user_data.get('savings', 0)
    months = user_data.get('months', {})
    
    if savings >= 100000 and 'savings_master' not in achievements:
        achievements['savings_master'] = {'name': 'Maître des Économies', 'date': datetime.now().isoformat()}
        user_data['points'] = user_data.get('points', 0) + 100
        st.balloons()
        st.markdown('<div class="success-alert">🎉 Badge débloqué : Maître des Économies ! +100 Pièces d’Or</div>', unsafe_allow_html=True)
    
    if len(months) >= 3 and 'loyal_hero' not in achievements:
        achievements['loyal_hero'] = {'name': 'Héros Fidèle', 'date': datetime.now().isoformat()}
        user_data['points'] = user_data.get('points', 0) + 50
        st.balloons()
        st.markdown('<div class="success-alert">🎉 Badge débloqué : Héros Fidèle ! +50 Pièces d’Or</div>', unsafe_allow_html=True)
    
    user_data['achievements'] = achievements
    budget_manager.update_user_data(username, user_data)

def apply_theme(theme):
    if theme == "Sombre":
        st.markdown("""
        <style>
            .stApp { background-color: #1a1a1a; color: #ffffff; }
            .metric-card { background: #2c2c2c; border-left: 4px solid #764ba2; }
            .budget-card { background: linear-gradient(135deg, #2c2c2c 0%, #4a4a4a 100%); }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "Fantasy":
        st.markdown("""
        <style>
            .stApp { background: url('https://cdn.pixabay.com/photo/2016/04/01/10/59/fantasy-1299587_1280.png'); background-size: cover; }
            .metric-card { background: rgba(255,255,255,0.8); border-left: 4px solid #d4a017; }
            .budget-card { background: rgba(200,200,255,0.9); }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: #000000; }
        </style>
        """, unsafe_allow_html=True)

def dashboard_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme142(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>📊 Tableau de Bord Épique</h1></div>', unsafe_allow_html=True)
    
    update_achievements(st.session_state.username, user_data)
    current_month = get_current_month_key()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="treasure-chest">
            <h3 style="color: #d4a017; margin: 0;">💰 Petit Coffre</h3>
            <h2 style="margin: 0; color: white;">{:,.0f} FCFA</h2>
        </div>
        """.format(user_data.get('savings', 0)), unsafe_allow_html=True)
    
    if current_month in user_data.get('months', {}):
        month_data = user_data['months'][current_month]
        total_budget = sum(month_data.get('budget', {}).values())
        total_spent = sum(month_data.get('expenses', {}).values())
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">📈 Budget Total</h3>
                <h2 style="margin: 0;">{:,.0f} FCFA</h2>
            </div>
            """.format(total_budget), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #ffc107; margin: 0;">💸 Dépenses</h3>
                <h2 style="margin: 0;">{:,.0f} FCFA</h2>
            </div>
            """.format(total_spent), unsafe_allow_html=True)
        
        with col4:
            remaining = total_budget - total_spent
            color = "#28a745" if remaining >= 0 else "#dc3545"
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: {}; margin: 0;">💎 Reste</h3>
                <h2 style="margin: 0; color: {}">{:,.0f} FCFA</h2>
            </div>
            """.format(color, color, remaining), unsafe_allow_html=True)
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            if month_data.get('budget'):
                fig = go.Figure(data=[
                    go.Scatter3d(
                        x=list(month_data['budget'].keys()),
                        y=[datetime.now().month] * len(month_data['budget']),
                        z=list(month_data['budget'].values()),
                        mode='markers+text',
                        marker=dict(size=12, color=list(month_data['budget'].values()), colorscale='Viridis'),
                        text=list(month_data['budget'].keys())
                    )
                ])
                fig.update_layout(
                    title="🌍 Budget 3D",
                    scene=dict(xaxis_title="Catégorie", yaxis_title="Mois", zaxis_title="Montant (FCFA)"),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if month_data.get('expenses'):
                fig = px.bar(
                    x=list(month_data['expenses'].keys()),
                    y=list(month_data['expenses'].values()),
                    title="Dépenses par Catégorie",
                    color=list(month_data['expenses'].values()),
                    color_continuous_scale="RdYlBu_r"
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Conseiller financier
        st.markdown("### 🧙‍♂️ Conseils du Sage Financier")
        for category in month_data.get('expenses', {}):
            if category in month_data.get('budget', {}) and month_data['expenses'][category] / month_data['budget'][category] > 0.8:
                st.markdown(f'<div class="warning-alert">⚠️ Attention à vos dépenses en {category} ! Essayez de cuisiner à la maison ou d’acheter en gros.</div>', unsafe_allow_html=True)
                break
        else:
            st.markdown('<div class="success-alert">👍 Vous gérez bien votre budget ! Continuez ainsi !</div>', unsafe_allow_html=True)
        
        # Narration financière
        st.markdown(f"""
        <div class="budget-card">
            <h3>📜 Votre Légende Financière</h3>
            <p>Chapitre {len(user_data.get('months', {}))}: <strong>La Quête du Petit Coffre</strong></p>
            <p>Le héros {st.session_state.username} a amassé {user_data.get('savings', 0):,.0f} FCFA dans son coffre légendaire !</p>
        </div>
        """, unsafe_allow_html=True)

def planning_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>📋 Planification Mensuelle</h1></div>', unsafe_allow_html=True)
    
    current_month = get_current_month_key()
    month_name = datetime.now().strftime("%B %Y")
    
    st.markdown(f"### 📅 Planification pour {month_name}")
    
    if current_month in user_data.get('months', {}):
        st.markdown('<div classr="warning-alert">⚠️ Vous avez déjà une planification pour ce mois.</div>', unsafe_allow_html=True)
        existing_budget = user_data['months'][current_month].get('budget', {})
    else:
        existing_budget = {}
    
    st.markdown('<div class="expense-form">', unsafe_allow_html=True)
    
    categories = get_categories()
    budget = {}
    
    col1, col2 = st.columns(2)
    
    for i, category in enumerate(categories):
        col = col1 if i % 2 == 0 else col2
        with col:
            budget[category] = st.number_input(
                f"💰 {category}",
                min_value=0,
                value=existing_budget.get(category, 0),
                step=1000,
                key=f"budget_{category}"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    total_budget = sum(budget.values())
    st.markdown(f"### 💎 Budget Total: {total_budget:,.0f} FCFA")
    
    if st.button("✅ Valider la planification", use_container_width=True):
        if total_budget > 0:
            if 'months' not in user_data:
                user_data['months'] = {}
            
            if current_month not in user_data['months']:
                user_data['months'][current_month] = {
                    'budget': {},
                    'expenses': {},
                    'expense_details': []
                }
            
            user_data['months'][current_month]['budget'] = budget
            user_data['points'] = user_data.get('points', 0) + 50  # Récompense pour planification
            budget_manager.update_user_data(st.session_state.username, user_data)
            st.markdown('<div class="success-alert">✅ Planification sauvegardée ! +50 Pièces d’Or</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("❌ Veuillez définir au moins un budget pour une catégorie")

def add_expense_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>💸 Ajouter une Dépense</h1></div>', unsafe_allow_html=True)
    
    current_month = get_current_month_key()
    
    if current_month not in user_data.get('months', {}):
        st.warning("⚠️ Créez d'abord une planification mensuelle.")
        return
    
    st.markdown('<div class="expense-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("🏷️ Catégorie", get_categories())
        amount = st.number_input("💰 Montant", min_value=0, step=100)
    
    with col2:
        description = st.text_area("📝 Description", height=100)
        expense_date = st.date_input("📅 Date", value=date.today())
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ Ajouter la dépense", use_container_width=True):
        if amount > 0 and description.strip():
            month_data = user_data['months'][current_month]
            
            if 'expenses' not in month_data:
                month_data['expenses'] = {}
            if 'expense_details' not in month_data:
                month_data['expense_details'] = []
            
            if category not in month_data['expenses']:
                month_data['expenses'][category] = 0
            
            month_data['expenses'][category] += amount
            month_data['expense_details'].append({
                'category': category,
                'amount': amount,
                'description': description,
                'date': expense_date.isoformat(),
                'timestamp': datetime.now().isoformat()
            })
            
            user_data['points'] = user_data.get('points', 0) + 10  # Récompense pour ajout
            budget_manager.update_user_data(st.session_state.username, user_data)
            
            st.markdown('<div class="success-alert">✅ Dépense ajoutée ! +10 Pièces d’Or</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("❌ Veuillez remplir tous les champs")

def manage_income_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>💰 Gérer les Entrées</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="treasure-chest">
            <h3 style="color: #d4a017; margin: 0;">💰 Petit Coffre</h3>
            <h2 style="margin: 0; color: white;">{:,.0f} FCFA</h2>
        </div>
        """.format(user_data.get('savings', 0)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Ajouter une entrée", "📊 Répartir l'argent", "🏦 Connexion Bancaire"])
    
    with tab1:
        st.markdown('<div class="expense-form">', unsafe_allow_html=True)
        
        income_amount = st.number_input("💰 Montant de l'entrée", min_value=0, step=1000)
        income_description = st.text_input("📝 Description de l'entrée")
        
        if st.button("💰 Ajouter au petit coffre"):
            if income_amount > 0:
                user_data['savings'] = user_data.get('savings', 0) + income_amount
                user_data['points'] = user_data.get('points', 0) + 20
                budget_manager.update_user_data(st.session_state.username, user_data)
                st.markdown('<div class="success-alert">✅ Entrée ajoutée ! +20 Pièces d’Or</div>', unsafe_allow_html=True)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        current_month = get_current_month_key()
        if current_month in user_data.get('months', {}) and user_data.get('savings', 0) > 0:
            st.markdown('<div class="expense-form">', unsafe_allow_html=True)
            
            st.markdown("### 📊 Répartir l'argent du petit coffre")
            categories = get_categories()
            
            allocation = {}
            total_allocation = 0
            
            for category in categories:
                allocation[category] = st.number_input(
                    f"💰 Ajouter à {category}",
                    min_value=0,
                    max_value=user_data.get('savings', 0),
                    step=1000,
                    key=f"alloc_{category}"
                )
                total_allocation += allocation[category]
            
            st.markdown(f"**💎 Total à répartir: {total_allocation:,.0f} FCFA**")
            st.markdown(f"**💰 Reste dans le coffre: {user_data.get('savings', 0) - total_allocation:,.0f} FCFA**")
            
            if st.button("✅ Confirmer la répartition"):
                if total_allocation <= user_data.get('savings', 0):
                    month_data = user_data['months'][current_month]
                    
                    for category, amount in allocation.items():
                        if amount > 0:
                            if category not in month_data['budget']:
                                month_data['budget'][category] = 0
                            month_data['budget'][category] += amount
                    
                    user_data['savings'] -= total_allocation
                    user_data['points'] = user_data.get('points', 0) + 30
                    budget_manager.update_user_data(st.session_state.username, user_data)
                    st.markdown('<div class="success-alert">✅ Répartition effectuée ! +30 Pièces d’Or</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("❌ Le montant total dépasse le montant disponible")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ Créez une planification mensuelle et ajoutez de l'argent au coffre")
    
    with tab3:
        st.markdown('<div class="expense-form"><h3>🏦 Connexion Bancaire</h3></div>', unsafe_allow_html=True)
        bank_api_key = st.text_input("🔑 Clé API bancaire", type="password")
        if st.button("🔗 Connecter"):
            st.success("✅ Compte bancaire connecté (simulation) !")

def monthly_tracking_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>📈 Suivi du Mois Actuel</h1></div>', unsafe_allow_html=True)
    
    current_month = get_current_month_key()
    month_name = datetime.now().strftime("%B %Y")
    
    if current_month not in user_data.get('months', {}):
        st.warning("⚠️ Aucune planification pour ce mois.")
        return
    
    month_data = user_data['months'][current_month]
    budget = month_data.get('budget', {})
    expenses = month_data.get('expenses', {})
    
    st.markdown(f"### 📅 Suivi pour {month_name}")
    
    tracking_data = []
    for category in get_categories():
        budgeted = budget.get(category, 0)
        spent = expenses.get(category, 0)
        remaining = budgeted - spent
        
        if budgeted > 0:
            percentage = (spent / budgeted) * 100
            if percentage <= 80:
                status = "🟢 Excellent"
                status_color = "#28a745"
            elif percentage <= 100:
                status = "🟡 Attention"
                status_color = "#ffc107"
            else:
                status = "🔴 Dépassé"
                status_color = "#dc3545"
        else:
            status = "⚪ Non défini"
            status_color = "#6c757d"
            percentage = 0
        
        tracking_data.append({
            'Catégorie': category,
            'Budget': f"{budgeted:,.0f} FCFA",
            'Dépensé': f"{spent:,.0f} FCFA",
            'Reste': f"{remaining:,.0f} FCFA",
            'Status': status
        })
    
    for data in tracking_data:
        if data['Budget'] != "0 FCFA":
            category = data['Catégorie']
            budgeted = budget.get(category, 0)
            spent = expenses.get(category, 0)
            remaining = budgeted - spent
            
            progress = min((spent / budgeted) * 100, 100) if budgeted > 0 else 0
            
            if progress <= 80:
                color = "#28a745"
            elif progress <= 100:
                color = "#ffc107"
            else:
                color = "#dc3545"
            
            st.markdown(f"""
            <div class="budget-card">
                <h3 style="margin: 0; color: #343a40;">💰 {category}</h3>
                <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                    <span><strong>Budget:</strong> {budgeted:,.0f} FCFA</span>
                    <span><strong>Dépensé:</strong> {spent:,.0f} FCFA</span>
                    <span><strong>Reste:</strong> <span style="color: {color};">{remaining:,.0f} FCFA</span></span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 10px; margin: 1rem 0;">
                    <div style="background: {color}; height: 100%; width: {min(progress, 100)}%; border-radius: 10px; transition: width 0.3s;"></div>
                </div>
                <div style="text-align: center; font-weight: bold; color: {color};">{progress:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    if month_data.get('expense_details'):
        st.markdown("---")
        st.markdown("### 📋 Dépenses Récentes")
        
        recent_expenses = sorted(
            month_data['expense_details'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]
        
        for expense in recent_expenses:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #667eea;">
                <strong>{expense['category']}</strong> - {expense['amount']:,.0f} FCFA<br>
                <small>{expense['description']} • {expense['date']}</small>
            </div>
            """, unsafe_allow_html=True)

def history_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>📚 Historique des Mois</h1></div>', unsafe_allow_html=True)
    
    months = user_data.get('months', {})
    
    if not months:
        st.info("ℹ️ Aucun historique disponible.")
        return
    
    month_options = {}
    for month_key in sorted(months.keys(), reverse=True):
        try:
            month_date = datetime.strptime(month_key, "%Y-%m")
            month_name = month_date.strftime("%B %Y")
            month_options[month_name] = month_key
        except:
            continue
    
    if not month_options:
        st.info("ℹ️ Aucun historique valide trouvé.")
        return
    
    selected_month_name = st.selectbox("📅 Choisir un mois", list(month_options.keys()))
    selected_month = month_options[selected_month_name]
    
    month_data = months[selected_month]
    budget = month_data.get('budget', {})
    expenses = month_data.get('expenses', {})
    
    total_budget = sum(budget.values())
    total_spent = sum(expenses.values())
    difference = total_budget - total_spent
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea; margin: 0;">Budget Alloué</h4>
            <h3 style="margin: 0;">{:,.0f} FCFA</h3>
        </div>
        """.format(total_budget), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #ffc107; margin: 0;">Dépenses Réalisées</h4>
            <h3 style="margin: 0;">{:,.0f} FCFA</h3>
        </div>
        """.format(total_spent), unsafe_allow_html=True)
    
    with col3:
        color = "#28a745" if difference >= 0 else "#dc3545"
        label = "Économies Réalisées" if difference >= 0 else "Dépassement"
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: {}; margin: 0;">{}</h4>
            <h3 style="margin: 0; color: {}">{:,.0f} FCFA</h3>
        </div>
        """.format(color, label, color, abs(difference)), unsafe_allow_html=True)
    
    with col4:
        percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #17a2b8; margin: 0;">Taux d'Utilisation</h4>
            <h3 style="margin: 0;">{:.1f}%</h3>
        </div>
        """.format(percentage), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if budget:
            fig = px.bar(
                x=list(budget.keys()),
                y=list(budget.values()),
                title="Budget vs Dépenses",
                color_discrete_sequence=['#667eea']
            )
            if expenses:
                fig.add_bar(
                    x=list(expenses.keys()),
                    y=list(expenses.values()),
                    name="Dépenses",
                    marker_color='#ffc107'
                )
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if expenses:
            fig = px.pie(
                values=list(expenses.values()),
                names=list(expenses.keys()),
                title="Répartition des Dépenses",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    if month_data.get('expense_details'):
        st.markdown("---")
        st.markdown("### 📋 Détail des Transactions")
        
        expense_details = month_data.get('expense_details', [])
        df = pd.DataFrame(expense_details)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
            
            st.dataframe(
                df[['date', 'category', 'amount', 'description']].rename(columns={
                    'date': 'Date',
                    'category': 'Catégorie',
                    'amount': 'Montant (FCFA)',
                    'description': 'Description'
                }),
                use_container_width=True
            )

def quests_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>⚔️ Quêtes Financières</h1></div>', unsafe_allow_html=True)
    
    quests = [
        {"name": "Épargne Héroïque", "goal": "Ajouter 50 000 FCFA au Petit Coffre", "progress": user_data.get('savings', 0) / 50000},
        {"name": "Maîtrise Alimentaire", "goal": "Réduire les dépenses Nourriture de 10%", "progress": 0.4}
    ]
    
    for quest in quests:
        progress = min(quest['progress'], 1.0)
        if progress >= 1.0 and f"quest_{quest['name'].lower().replace(' ', '_')}" not in user_data.get('achievements', {}):
            user_data['achievements'][f"quest_{quest['name'].lower().replace(' ', '_')}"] = {
                'name': quest['name'],
                'date': datetime.now().isoformat()
            }
            user_data['points'] = user_data.get('points', 0) + 100
            budget_manager.update_user_data(st.session_state.username, user_data)
            st.balloons()
            st.markdown(f'<div class="success-alert">🎉 Quête complétée : {quest["name"]} ! +100 Pièces d’Or</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="budget-card">
            <h3>{quest['name']}</h3>
            <p>{quest['goal']}</p>
            <div style="background: #e9ecef; border-radius: 10px; height: 10px;">
                <div style="background: #28a745; height: 100%; width: {progress*100}%; border-radius: 10px;"></div>
            </div>
            <p>{progress*100:.1f}% complété</p>
        </div>
        """, unsafe_allow_html=True)

def advisor_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>🧙‍♂️ Conseiller Financier</h1></div>', unsafe_allow_html=True)
    
    current_month = get_current_month_key()
    month_data = user_data['months'].get(current_month, {})
    expenses = month_data.get('expenses', {})
    budget = month_data.get('budget', {})
    
    st.markdown("### 🧙‍♂️ Conseils du Sage Financier")
    tips = []
    for category in expenses:
        if category in budget and expenses[category] / budget[category] > 0.8:
            tips.append(f"⚠️ Attention à vos dépenses en {category} ! Essayez de réduire les sorties ou d'acheter en gros.")
    
    if tips:
        for tip in tips:
            st.markdown(f'<div class="warning-alert">{tip}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-alert">👍 Vous gérez bien votre budget ! Continuez ainsi !</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔮 Prédictions des Dépenses")
    months = user_data.get('months', {})
    if len(months) >= 2:
        categories = get_categories()
        predictions = {cat: 0 for cat in categories}
        count = 0
        
        for month_data in months.values():
            for cat in categories:
                predictions[cat] += month_data.get('expenses', {}).get(cat, 0)
            count += 1
        
        for cat in predictions:
            predictions[cat] = predictions[cat] / count if count > 0 else 0
        
        for cat, amount in predictions.items():
            if amount > 0:
                st.markdown(f"📊 {cat}: environ {amount:,.0f} FCFA attendu ce mois-ci")
    else:
        st.info("ℹ️ Pas assez de données pour les prédictions.")

def academy_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>🏫 Académie Financière</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### 📚 Leçons")
    lessons = [
        {"title": "Les bases de l'épargne", "content": "Épargnez 10% de vos revenus chaque mois pour constituer un fonds d'urgence."},
        {"title": "Gérer les dettes", "content": "Priorisez le remboursement des dettes à taux d'intérêt élevé."}
    ]
    
    for lesson in lessons:
        with st.expander(lesson['title']):
            st.write(lesson['content'])
    
    st.markdown("### 🧠 Quiz Financier")
    question = "Quel est le meilleur moyen d'épargner ?"
    options = ["Dépenser tout immédiatement", "Épargner 10% chaque mois", "Ne rien épargner"]
    answer = st.radio(question, options)
    if st.button("Vérifier"):
        if answer == "Épargner 10% chaque mois":
            user_data['points'] = user_data.get('points', 0) + 20
            budget_manager.update_user_data(st.session_state.username, user_data)
            st.success("🎉 Correct ! +20 Pièces d’Or")
        else:
            st.error("❌ Essayez encore !")

def settings_page():
    user_data = budget_manager.get_user_data(st.session_state.username)
    apply_theme(user_data.get('theme', 'Clair'))
    st.markdown('<div class="main-header"><h1>⚙️ Paramètres</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profil", "🔄 Gestion des Données", "📊 Statistiques", "🎨 Personnalisation"])
    
    with tab1:
        st.markdown("### 👤 Informations du Profil")
        st.info(f"👤 Utilisateur: {st.session_state.username}")
        st.info(f"💰 Petit Coffre: {user_data.get('savings', 0):,.0f} FCFA")
        st.info(f"🌟 Pièces d’Or: {user_data.get('points', 0)}")
        months_count = len(user_data.get('months', {}))
        st.info(f"📅 Mois gérés: {months_count}")
        
        st.markdown("### 🏆 Réalisations")
        for ach_id, ach in user_data.get('achievements', {}).items():
            st.markdown(f"🏅 {ach['name']} - Obtenu le {ach['date'][:10]}")
    
    with tab2:
        st.markdown("### 🔄 Gestion des Données")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exporter les données", use_container_width=True):
                data_json = json.dumps(user_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Télécharger JSON",
                    data=data_json,
                    file_name=f"budget_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📤 Partager votre progrès"):
                img = Image.new('RGB', (400, 200), color='#667eea')
                draw = ImageDraw.Draw(img)
                draw.text((20, 20), f"Budget de {st.session_state.username} - {datetime.now().strftime('%B %Y')}", fill='white')
                draw.text((20, 60), f"Petit Coffre: {user_data.get('savings', 0):,.0f} FCFA", fill='white')
                draw.text((20, 100), f"Pièces d’Or: {user_data.get('points', 0)}", fill='white')
                img.save("budget_share.png")
                st.image("budget_share.png")
                with open("budget_share.png", "rb") as file:
                    st.download_button("📤 Télécharger l'image", file, file_name="budget_share.png")
        
        st.markdown("---")
        st.markdown("#### 🗑️ Zone Dangereuse")
        if st.button("🗑️ Réinitialiser le petit coffre", type="secondary"):
            if st.session_state.get('confirm_reset_savings'):
                user_data['savings'] = 0
                budget_manager.update_user_data(st.session_state.username, user_data)
                st.session_state['confirm_reset_savings'] = False
                st.success("✅ Petit coffre réinitialisé !")
                st.rerun()
            else:
                st.session_state['confirm_reset_savings'] = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")
        
        if st.button("💥 Supprimer toutes les données", type="secondary"):
            if st.session_state.get('confirm_delete_all'):
                user_data = {'months': {}, 'savings': 0, 'achievements': {}, 'avatar': 'Chevalier', 'points': 0, 'theme': 'Clair'}
                budget_manager.update_user_data(st.session_state.username, user_data)
                st.session_state['confirm_delete_all'] = False
                st.success("✅ Données supprimées !")
                st.rerun()
            else:
                st.session_state['confirm_delete_all'] = True
                st.error("⚠️ Action irréversible ! Cliquez à nouveau pour confirmer.")
    
    with tab3:
        st.markdown("### 📊 Statistiques Générales")
        months = user_data.get('months', {})
        if months:
            total_months = len(months)
            total_budgets = []
            total_expenses = []
            
            for month_data in months.values():
                total_budgets.append(sum(month_data.get('budget', {}).values()))
                total_expenses.append(sum(month_data.get('expenses', {}).values()))
            
            avg_budget = sum(total_budgets) / len(total_budgets) if total_budgets else 0
            avg_expenses = sum(total_expenses) / len(total_expenses) if total_expenses else 0
            total_savings = sum(b - e for b, e in zip(total_budgets, total_expenses))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #667eea; margin: 0;">📅 Mois Gérés</h4>
                    <h3 style="margin: 0;">{}</h3>
                </div>
                """.format(total_months), unsafe_allow_html=True)
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #28a745; margin: 0;">💰 Budget Moyen</h4>
                    <h3 style="margin: 0;">{:,.0f} FCFA</h3>
                </div>
                """.format(avg_budget), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #ffc107; margin: 0;">💸 Dépenses Moyennes</h4>
                    <h3 style="margin: 0;">{:,.0f} FCFA</h3>
                </div>
                """.format(avg_expenses), unsafe_allow_html=True)
                color = "#28a745" if total_savings >= 0 else "#dc3545"
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: {}; margin: 0;">💎 Économies Totales</h4>
                    <h3 style="margin: 0; color: {}">{:,.0f} FCFA</h3>
                </div>
                """.format(color, color, total_savings), unsafe_allow_html=True)
            
            if len(months) > 1:
                months_sorted = sorted(months.items())
                month_names = []
                budgets = []
                expenses = []
                
                for month_key, month_data in months_sorted:
                    try:
                        month_date = datetime.strptime(month_key, "%Y-%m")
                        month_names.append(month_date.strftime("%b %Y"))
                        budgets.append(sum(month_data.get('budget', {}).values()))
                        expenses.append(sum(month_data.get('expenses', {}).values()))
                    except:
                        continue
                
                if month_names:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=month_names,
                        y=budgets,
                        mode='lines+markers',
                        name='Budget',
                        line=dict(color='#667eea', width=3)
                    ))
                    fig.add_trace(go.Scatter(
                        x=month_names,
                        y=expenses,
                        mode='lines+markers',
                        name='Dépenses',
                        line=dict(color='#ffc107', width=3)
                    ))
                    fig.update_layout(
                        title="Évolution Budget vs Dépenses",
                        xaxis_title="Mois",
                        yaxis_title="Montant (FCFA)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Aucune donnée pour les statistiques.")
    
    with tab4:
        st.markdown("### 🎨 Personnalisation")
        avatars = ["Chevalier", "Astronaute", "Dragon", "Sorcier"]
        selected_avatar = st.selectbox("🎭 Avatar", avatars, index=avatars.index(user_data.get('avatar', 'Chevalier')))
        user_data['avatar'] = selected_avatar
        
        themes = ["Clair", "Sombre", "Fantasy"]
        selected_theme = st.selectbox("🎨 Thème", themes, index=themes.index(user_data.get('theme', 'Clair')))
        user_data['theme'] = selected_theme
        
        budget_manager.update_user_data(st.session_state.username, user_data)
        
        st.markdown("### 🌌 Réalité Augmentée (Bientôt Disponible)")
        st.markdown("""
        <div class="budget-card">
            <h3>🌌 Visualisez votre budget en AR !</h3>
            <p>Bientôt : Découvrez votre Petit Coffre en 3D dans votre environnement !</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        page = sidebar_navigation()
        
        if page == "dashboard":
            dashboard_page()
        elif page == "planning":
            planning_page()
        elif page == "add_expense":
            add_expense_page()
        elif page == "manage_income":
            manage_income_page()
        elif page == "monthly_tracking":
            monthly_tracking_page()
        elif page == "history":
            history_page()
        elif page == "quests":
            quests_page()
        elif page == "advisor":
            advisor_page()
        elif page == "academy":
            academy_page()
        elif page == "settings":
            settings_page()

budget_manager = BudgetManager()

if __name__ == "__main__":
    main()