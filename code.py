import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import hashlib
from pathlib import Path

st.set_page_config(
    page_title="💰 Mon Budget Personnel",
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
            'savings': 0
        }
        self.save_data()
        return True
    
    def authenticate(self, username, password):
        if username not in self.users:
            return False
        return self.users[username] == self.hash_password(password)
    
    def get_user_data(self, username):
        return self.data.get(username, {'months': {}, 'savings': 0})
    
    def update_user_data(self, username, data):
        self.data[username] = data
        self.save_data()

def login_page():
    st.markdown('<div class="main-header"><h1>💰 Mon Budget Personnel</h1><p>Gérez vos finances en toute simplicité</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
    
    with tab1:
        st.markdown("### Connectez-vous à votre compte")
        username = st.text_input("👤 Nom d'utilisateur", key="login_user")
        password = st.text_input("🔒 Mot de passe", type="password", key="login_pass")
        
        if st.button("Se connecter", use_container_width=True):
            if budget_manager.authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Connexion réussie!")
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
    
    with tab2:
        st.markdown("### Créer un nouveau compte")
        new_username = st.text_input("👤 Nom d'utilisateur", key="reg_user")
        new_password = st.text_input("🔒 Mot de passe", type="password", key="reg_pass")
        confirm_password = st.text_input("🔒 Confirmer le mot de passe", type="password", key="reg_confirm")
        
        if st.button("S'inscrire", use_container_width=True):
            if new_password != confirm_password:
                st.error("❌ Les mots de passe ne correspondent pas")
            elif len(new_password) < 4:
                st.error("❌ Le mot de passe doit contenir au moins 4 caractères")
            elif budget_manager.register_user(new_username, new_password):
                st.success("✅ Compte créé avec succès! Vous pouvez maintenant vous connecter.")
            else:
                st.error("❌ Ce nom d'utilisateur existe déjà")

def sidebar_navigation():
    st.sidebar.markdown(f"### 👋 Bonjour, {st.session_state.username}!")
    
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
        "⚙️ Paramètres": "settings"
    }
    
    selected = st.sidebar.radio("Navigation", list(pages.keys()))
    return pages[selected]

def get_current_month_key():
    return datetime.now().strftime("%Y-%m")

def get_categories():
    return ["Transport", "Nourriture", "Factures", "Santé", "Divers"]

def dashboard_page():
    st.markdown('<div class="main-header"><h1>📊 Tableau de bord</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    current_month = get_current_month_key()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">💰 Petit Coffre</h3>
            <h2 style="margin: 0;">{:,.0f} FCFA</h2>
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
                fig = px.pie(
                    values=list(month_data['budget'].values()),
                    names=list(month_data['budget'].keys()),
                    title="Répartition du Budget",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(showlegend=True, height=400)
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

def planning_page():
    st.markdown('<div class="main-header"><h1>📋 Planification Mensuelle</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    current_month = get_current_month_key()
    month_name = datetime.now().strftime("%B %Y")
    
    st.markdown(f"### 📅 Planification pour {month_name}")
    
    if current_month in user_data.get('months', {}):
        st.markdown("""
        <div class="warning-alert">
            ⚠️ Vous avez déjà une planification pour ce mois. Vous pouvez la modifier ci-dessous.
        </div>
        """, unsafe_allow_html=True)
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
            budget_manager.update_user_data(st.session_state.username, user_data)
            
            st.markdown("""
            <div class="success-alert">
                ✅ Planification sauvegardée avec succès!
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("❌ Veuillez définir au moins un budget pour une catégorie")

def add_expense_page():
    st.markdown('<div class="main-header"><h1>💸 Ajouter une Dépense</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    current_month = get_current_month_key()
    
    if current_month not in user_data.get('months', {}):
        st.warning("⚠️ Veuillez d'abord créer une planification pour ce mois dans la section 'Planification mensuelle'.")
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
            
            budget_manager.update_user_data(st.session_state.username, user_data)
            
            st.markdown("""
            <div class="success-alert">
                ✅ Dépense ajoutée avec succès!
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("❌ Veuillez remplir tous les champs avec des valeurs valides")

def manage_income_page():
    st.markdown('<div class="main-header"><h1>💰 Gérer les Entrées d\'Argent</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">💰 Petit Coffre</h3>
            <h2 style="margin: 0;">{user_data.get('savings', 0):,.0f} FCFA</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["➕ Ajouter une entrée", "📊 Répartir l'argent"])
    
    with tab1:
        st.markdown('<div class="expense-form">', unsafe_allow_html=True)
        
        income_amount = st.number_input("💰 Montant de l'entrée", min_value=0, step=1000)
        income_description = st.text_input("📝 Description de l'entrée")
        
        if st.button("💰 Ajouter au petit coffre"):
            if income_amount > 0:
                user_data['savings'] = user_data.get('savings', 0) + income_amount
                budget_manager.update_user_data(st.session_state.username, user_data)
                
                st.markdown("""
                <div class="success-alert">
                    ✅ Entrée ajoutée au petit coffre!
                </div>
                """, unsafe_allow_html=True)
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
                    budget_manager.update_user_data(st.session_state.username, user_data)
                    
                    st.markdown("""
                    <div class="success-alert">
                        ✅ Répartition effectuée avec succès!
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("❌ Le montant total dépasse le montant disponible dans le coffre")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ Créez d'abord une planification mensuelle et ajoutez de l'argent au petit coffre")

def monthly_tracking_page():
    st.markdown('<div class="main-header"><h1>📈 Suivi du Mois Actuel</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    current_month = get_current_month_key()
    month_name = datetime.now().strftime("%B %Y")
    
    if current_month not in user_data.get('months', {}):
        st.warning("⚠️ Aucune planification trouvée pour ce mois. Créez d'abord votre planification mensuelle.")
        return
    
    month_data = user_data['months'][current_month]
    budget = month_data.get('budget', {})
    expenses = month_data.get('expenses', {})
    
    st.markdown(f"### 📅 Suivi pour {month_name}")
    
    # Tableau de suivi
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
    
    # Affichage sous forme de cartes
    for data in tracking_data:
        if data['Budget'] != "0 FCFA":  # N'afficher que les catégories avec budget
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
    
    # Historique des dépenses récentes
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
    st.markdown('<div class="main-header"><h1>📚 Historique des Mois</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    months = user_data.get('months', {})
    
    if not months:
        st.info("ℹ️ Aucun historique disponible. Commencez par créer votre première planification mensuelle.")
        return
    
    # Sélecteur de mois
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
    
    # Résumé du mois
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
    
    # Détails par catégorie
    st.markdown("---")
    st.markdown("### 📊 Détails par Catégorie")
    
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
    
    # Détail des transactions
    if month_data.get('expense_details'):
        st.markdown("---")
        st.markdown("### 📋 Détail des Transactions")
        
        expense_details = month_data['expense_details']
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

def settings_page():
    st.markdown('<div class="main-header"><h1>⚙️ Paramètres</h1></div>', unsafe_allow_html=True)
    
    user_data = budget_manager.get_user_data(st.session_state.username)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profil", "🔄 Gestion des Données", "📊 Statistiques"])
    
    with tab1:
        st.markdown("### 👤 Informations du Profil")
        st.info(f"👤 Utilisateur: {st.session_state.username}")
        st.info(f"💰 Petit Coffre: {user_data.get('savings', 0):,.0f} FCFA")
        
        months_count = len(user_data.get('months', {}))
        st.info(f"📅 Nombre de mois gérés: {months_count}")
        
        if st.button("🔄 Changer de mot de passe"):
            st.info("Cette fonctionnalité sera disponible dans une prochaine version.")
    
    with tab2:
        st.markdown("### 🔄 Gestion des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exporter les données", use_container_width=True):
                data_json = json.dumps(user_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Télécharger le fichier JSON",
                    data=data_json,
                    file_name=f"budget_data_{st.session_state.username}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🗑️ Réinitialiser le petit coffre", use_container_width=True):
                if st.session_state.get('confirm_reset_savings'):
                    user_data['savings'] = 0
                    budget_manager.update_user_data(st.session_state.username, user_data)
                    st.session_state['confirm_reset_savings'] = False
                    st.success("✅ Petit coffre réinitialisé!")
                    st.rerun()
                else:
                    st.session_state['confirm_reset_savings'] = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer")
        
        st.markdown("---")
        st.markdown("#### 🗑️ Zone Dangereuse")
        
        if st.button("💥 Supprimer toutes les données", type="secondary"):
            if st.session_state.get('confirm_delete_all'):
                user_data = {'months': {}, 'savings': 0}
                budget_manager.update_user_data(st.session_state.username, user_data)
                st.session_state['confirm_delete_all'] = False
                st.success("✅ Toutes les données ont été supprimées!")
                st.rerun()
            else:
                st.session_state['confirm_delete_all'] = True
                st.error("⚠️ ATTENTION: Cette action est irréversible! Cliquez à nouveau pour confirmer.")
    
    with tab3:
        st.markdown("### 📊 Statistiques Générales")
        
        months = user_data.get('months', {})
        if months:
            # Calcul des statistiques
            total_months = len(months)
            total_budgets = []
            total_expenses = []
            
            for month_data in months.values():
                budget = month_data.get('budget', {})
                expenses = month_data.get('expenses', {})
                total_budgets.append(sum(budget.values()))
                total_expenses.append(sum(expenses.values()))
            
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
            
            # Graphique d'évolution
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
            st.info("ℹ️ Aucune donnée disponible pour les statistiques.")

# Fonction principale
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
        elif page == "settings":
            settings_page()

# Initialisation du gestionnaire de budget
budget_manager = BudgetManager()

if __name__ == "__main__":
    main()