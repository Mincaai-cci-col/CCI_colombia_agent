"""
Gestionnaire de contacts WhatsApp pour l'agent CCI
Permet de charger et rechercher les informations d'entreprises à partir d'une base de données Excel
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
import re

class ContactsManager:
    """
    Gestionnaire pour la base de données de contacts WhatsApp.
    Charge un fichier Excel et permet la recherche par numéro de téléphone.
    """
    
    def __init__(self, excel_file_path: str = None):
        """
        Initialise le gestionnaire de contacts.
        
        Args:
            excel_file_path: Chemin vers le fichier Excel de contacts
        """
        self.excel_file_path = excel_file_path
        self.contacts_df = None
        self.contacts_loaded = False
        
        # Correspondance des colonnes (peut être adaptée selon votre fichier)
        self.column_mapping = {
            'empresa': 'Empresa',
            'nombre': 'Nombre', 
            'apellido': 'Apellido',
            'celular': 'Celular',
            'cargo': 'Cargo',
            'sector': 'Sector de Actividad',
            'descripcion': 'Descripción'
        }
        
        # Charger automatiquement si le fichier est spécifié
        if excel_file_path:
            self.load_contacts()
    
    def load_contacts(self, excel_file_path: str = None) -> bool:
        """
        Charge la base de données de contacts depuis un fichier Excel.
        
        Args:
            excel_file_path: Chemin vers le fichier Excel (optionnel si déjà défini)
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        if excel_file_path:
            self.excel_file_path = excel_file_path
            
        if not self.excel_file_path:
            print("⚠️ Aucun fichier Excel spécifié pour les contacts")
            return False
            
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(self.excel_file_path):
                print(f"⚠️ Fichier contacts non trouvé : {self.excel_file_path}")
                return False
            
            # Charger le fichier Excel
            print(f"📊 Chargement des contacts depuis : {self.excel_file_path}")
            self.contacts_df = pd.read_excel(self.excel_file_path)
            
            # Vérifier que les colonnes essentielles sont présentes
            required_columns = ['Celular']  # Colonne minimale requise
            missing_columns = [col for col in required_columns if col not in self.contacts_df.columns]
            
            if missing_columns:
                print(f"⚠️ Colonnes manquantes dans le fichier Excel : {missing_columns}")
                return False
            
            # Nettoyer les numéros de téléphone
            self.contacts_df['Celular_Clean'] = self.contacts_df['Celular'].apply(self._clean_phone_number)
            
            self.contacts_loaded = True
            print(f"✅ {len(self.contacts_df)} contacts chargés avec succès")
            
            # Afficher un aperçu des colonnes disponibles
            print(f"📋 Colonnes disponibles : {list(self.contacts_df.columns)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des contacts : {e}")
            self.contacts_loaded = False
            return False
    
    def _clean_phone_number(self, phone: str) -> str:
        """
        Nettoie un numéro de téléphone pour faciliter la recherche.
        
        Args:
            phone: Numéro de téléphone brut
            
        Returns:
            str: Numéro nettoyé (que les chiffres)
        """
        if pd.isna(phone):
            return ""
        
        # Convertir en string et garder seulement les chiffres
        phone_str = str(phone)
        cleaned = re.sub(r'[^\d]', '', phone_str)
        
        return cleaned
    
    def find_contact_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Recherche un contact par numéro de téléphone.
        
        Args:
            phone_number: Numéro de téléphone à rechercher
            
        Returns:
            Dict avec les informations du contact ou None si non trouvé
        """
        if not self.contacts_loaded or self.contacts_df is None:
            print("⚠️ Base de données de contacts non chargée")
            return None
        
        # Nettoyer le numéro de recherche
        clean_search_number = self._clean_phone_number(phone_number)
        
        if not clean_search_number:
            return None
        
        # Rechercher dans la base
        # Essayer une correspondance exacte d'abord
        exact_match = self.contacts_df[self.contacts_df['Celular_Clean'] == clean_search_number]
        
        if not exact_match.empty:
            return self._format_contact_info(exact_match.iloc[0])
        
        # Si pas de correspondance exacte, essayer une correspondance partielle
        # (les derniers 10 chiffres par exemple)
        if len(clean_search_number) >= 10:
            last_digits = clean_search_number[-10:]
            partial_match = self.contacts_df[self.contacts_df['Celular_Clean'].str.endswith(last_digits)]
            
            if not partial_match.empty:
                return self._format_contact_info(partial_match.iloc[0])
        
        # Essayer aussi avec les premiers chiffres pour les numéros internationaux
        if len(clean_search_number) >= 10:
            first_digits = clean_search_number[:10]
            partial_match = self.contacts_df[self.contacts_df['Celular_Clean'].str.contains(first_digits, na=False)]
            
            if not partial_match.empty:
                return self._format_contact_info(partial_match.iloc[0])
        
        return None
    
    def _format_contact_info(self, contact_row) -> Dict[str, Any]:
        """
        Formate les informations d'un contact pour l'agent.
        
        Args:
            contact_row: Ligne pandas avec les données du contact
            
        Returns:
            Dict avec les informations formatées
        """
        info = {}
        
        # Mapper les colonnes disponibles
        available_columns = contact_row.index.tolist()
        
        for key, column_name in self.column_mapping.items():
            if column_name in available_columns:
                value = contact_row[column_name]
                if pd.notna(value) and str(value).strip():
                    info[key] = str(value).strip()
        
        return info
    
    def get_contact_context_string(self, phone_number: str) -> str:
        """
        Génère une chaîne de contexte formatée pour l'agent à partir d'un numéro.
        
        Args:
            phone_number: Numéro de téléphone WhatsApp
            
        Returns:
            str: Contexte formaté pour l'agent ou chaîne vide si pas trouvé
        """
        contact_info = self.find_contact_by_phone(phone_number)
        
        if not contact_info:
            return ""
        
        # Générer le contexte en français et espagnol
        context_parts = []
        
        # Informations de base
        if 'empresa' in contact_info:
            context_parts.append(f"Entreprise/Empresa: {contact_info['empresa']}")
        
        if 'nombre' in contact_info and 'apellido' in contact_info:
            context_parts.append(f"Contact: {contact_info['nombre']} {contact_info['apellido']}")
        elif 'nombre' in contact_info:
            context_parts.append(f"Contact: {contact_info['nombre']}")
        
        if 'cargo' in contact_info:
            context_parts.append(f"Poste/Cargo: {contact_info['cargo']}")
        
        if 'sector' in contact_info:
            context_parts.append(f"Secteur/Sector: {contact_info['sector']}")
        
        if 'descripcion' in contact_info:
            context_parts.append(f"Description/Descripción: {contact_info['descripcion']}")
        
        if context_parts:
            header = "=== INFORMATIONS CLIENT / INFORMACIÓN DEL CLIENTE ==="
            footer = "=== FIN INFORMATIONS CLIENT / FIN INFORMACIÓN DEL CLIENTE ==="
            context = f"\n{header}\n" + "\n".join(context_parts) + f"\n{footer}\n"
            return context
        
        return ""



# Instance globale pour l'agent (singleton pattern)
_contacts_manager_instance = None

def get_contacts_manager(excel_file_path: str = None) -> ContactsManager:
    """
    Retourne l'instance globale du gestionnaire de contacts.
    
    Args:
        excel_file_path: Chemin vers le fichier Excel (pour l'initialisation)
        
    Returns:
        ContactsManager: Instance du gestionnaire
    """
    global _contacts_manager_instance
    
    if _contacts_manager_instance is None:
        _contacts_manager_instance = ContactsManager(excel_file_path)
    elif excel_file_path and not _contacts_manager_instance.contacts_loaded:
        _contacts_manager_instance.load_contacts(excel_file_path)
    
    return _contacts_manager_instance

def init_contacts_database(excel_file_path: str) -> bool:
    """
    Initialise la base de données de contacts.
    
    Args:
        excel_file_path: Chemin vers le fichier Excel
        
    Returns:
        bool: True si l'initialisation a réussi
    """
    manager = get_contacts_manager(excel_file_path)
    return manager.contacts_loaded 