import streamlit as st
import json
# import chromadb  # Commented out due to build issues
# from sentence_transformers import SentenceTransformer  # Commented out due to dependency issues
import numpy as np
from typing import List, Dict, Any, Tuple
import os
from utils.text_processing import TextProcessor

class PersonaSearch:
    """Natural Language Persona Search with Vector Database"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Commented out due to dependency issues
        # self.chroma_client = chromadb.Client()  # Commented out due to build issues
        # self.collection = None  # Commented out due to build issues
        self.personas = []
        # self.persona_embeddings = []  # Store embeddings in memory
        self.load_personas()
        self.initialize_vector_db()
    
    def load_personas(self):
        """Load sample personas from JSON file"""
        try:
            with open('data/sample_personas.json', 'r') as f:
                self.personas = json.load(f)
        except FileNotFoundError:
            st.error("Sample personas file not found. Please ensure data/sample_personas.json exists.")
            self.personas = []
    
    def initialize_vector_db(self):
        """Initialize simple text-based search system"""
        try:
            if self.personas:
                st.success(f"Initialized search system with {len(self.personas)} personas")
            else:
                st.warning("No personas loaded for search system initialization")
                
        except Exception as e:
            st.error(f"Error initializing search system: {e}")
    
    def create_persona_text_representation(self, persona: Dict[str, Any]) -> str:
        """Create a comprehensive text representation of a persona for embedding"""
        text_parts = [
            f"Name: {persona['name']}",
            f"Age: {persona['age']}",
            f"Location: {persona['location']}",
            f"Occupation: {persona['occupation']}",
            f"Interests: {', '.join(persona['interests'])}",
            f"Values: {', '.join(persona['values'])}",
            f"Personality: {', '.join(persona['personality'])}",
            f"Hobbies: {', '.join(persona['hobbies'])}",
            f"Goals: {', '.join(persona['goals'])}",
            f"Communication style: {persona['preferences']['communication_style']}",
            f"Meeting preference: {persona['preferences']['meeting_preference']}",
            f"Interests in others: {', '.join(persona['preferences']['interests_in_others'])}"
        ]
        return " | ".join(text_parts)
    
    def search_personas(self, query: str, preferences: Dict[str, Any] = None, 
                       exclusions: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search personas using simple text matching with preferences and exclusions
        """
        try:
            # Create enhanced query with preferences
            enhanced_query = self.enhance_query_with_preferences(query, preferences, exclusions)
            
            # Calculate text-based similarities with all personas
            similarities = []
            for i, persona in enumerate(self.personas):
                # Create text representation
                persona_text = self.create_persona_text_representation(persona).lower()
                query_lower = enhanced_query.lower()
                
                # Simple keyword matching
                score = 0
                for word in query_lower.split():
                    if word in persona_text:
                        score += 1
                
                # Normalize score
                similarity = score / max(len(query_lower.split()), 1)
                similarities.append((i, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Process and filter results
            filtered_results = self.filter_and_rank_results_simple(
                similarities, preferences, exclusions, top_k
            )
            
            return filtered_results
            
        except Exception as e:
            st.error(f"Error searching personas: {e}")
            return []
    
    def enhance_query_with_preferences(self, query: str, preferences: Dict[str, Any] = None, 
                                     exclusions: List[str] = None) -> str:
        """Enhance the search query with user preferences and exclusions"""
        enhanced_parts = [query]
        
        if preferences:
            if preferences.get('interests'):
                enhanced_parts.append(f"Interests: {', '.join(preferences['interests'])}")
            if preferences.get('values'):
                enhanced_parts.append(f"Values: {', '.join(preferences['values'])}")
            if preferences.get('location'):
                enhanced_parts.append(f"Location preference: {preferences['location']}")
            if preferences.get('age_range'):
                enhanced_parts.append(f"Age range: {preferences['age_range']}")
        
        if exclusions:
            enhanced_parts.append(f"Exclude: {', '.join(exclusions)}")
        
        return " | ".join(enhanced_parts)
    
    def filter_and_rank_results_simple(self, similarities: List[Tuple[int, float]], 
                                      preferences: Dict[str, Any] = None,
                                      exclusions: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Filter and rank search results based on preferences and exclusions"""
        filtered_results = []
        
        for persona_idx, similarity in similarities:
            # Get persona data
            persona = self.personas[persona_idx]
            
            # Check exclusions
            if exclusions and self.check_exclusions(persona, exclusions):
                continue
            
            # Calculate compatibility score
            compatibility_score = self.calculate_compatibility_score(
                persona, preferences, 1.0 - similarity  # Convert similarity to distance
            )
            
            # Add to filtered results
            filtered_results.append({
                'persona': persona,
                'compatibility_score': compatibility_score,
                'similarity_distance': 1.0 - similarity,
                'insights': self.generate_insights(persona, preferences),
                'action_points': self.generate_action_points(persona, preferences)
            })
        
        # Sort by compatibility score and return top k
        filtered_results.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return filtered_results[:top_k]
    
    def check_exclusions(self, persona: Dict[str, Any], exclusions: List[str]) -> bool:
        """Check if persona matches any exclusion criteria"""
        persona_text = self.create_persona_text_representation(persona).lower()
        for exclusion in exclusions:
            if exclusion.lower() in persona_text:
                return True
        return False
    
    def calculate_compatibility_score(self, persona: Dict[str, Any], 
                                   preferences: Dict[str, Any] = None,
                                   similarity_distance: float = 0.0) -> float:
        """Calculate compatibility score between persona and preferences"""
        base_score = 1.0 - similarity_distance  # Convert distance to similarity
        
        if not preferences:
            return base_score
        
        # Interest matching
        if preferences.get('interests'):
            interest_matches = sum(1 for interest in preferences['interests'] 
                                 if any(interest.lower() in p_interest.lower() 
                                       for p_interest in persona['interests']))
            interest_score = interest_matches / len(preferences['interests'])
            base_score *= (0.7 + 0.3 * interest_score)
        
        # Value matching
        if preferences.get('values'):
            value_matches = sum(1 for value in preferences['values'] 
                              if any(value.lower() in p_value.lower() 
                                    for p_value in persona['values']))
            value_score = value_matches / len(preferences['values'])
            base_score *= (0.8 + 0.2 * value_score)
        
        # Location preference
        if preferences.get('location') and persona['location']:
            if preferences['location'].lower() in persona['location'].lower():
                base_score *= 1.1
        
        # Age range preference
        if preferences.get('age_range') and persona['age']:
            min_age, max_age = preferences['age_range']
            if min_age <= persona['age'] <= max_age:
                base_score *= 1.05
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def generate_insights(self, persona: Dict[str, Any], 
                         preferences: Dict[str, Any] = None) -> str:
        """Generate insights about the persona match"""
        insights = []
        
        # Common interests
        if preferences and preferences.get('interests'):
            common_interests = [interest for interest in preferences['interests'] 
                              if any(interest.lower() in p_interest.lower() 
                                    for p_interest in persona['interests'])]
            if common_interests:
                insights.append(f"Shared interests: {', '.join(common_interests)}")
        
        # Communication style
        insights.append(f"Communication style: {persona['preferences']['communication_style']}")
        
        # Meeting preferences
        insights.append(f"Prefers to meet: {persona['preferences']['meeting_preference']}")
        
        # Personality highlights
        insights.append(f"Key traits: {', '.join(persona['personality'][:3])}")
        
        return "; ".join(insights)
    
    def generate_action_points(self, persona: Dict[str, Any], 
                             preferences: Dict[str, Any] = None) -> List[str]:
        """Generate actionable points for connecting with the persona"""
        action_points = []
        
        # Suggest meeting location
        action_points.append(f"Meet at: {persona['preferences']['meeting_preference']}")
        
        # Conversation starters
        if persona['hobbies']:
            action_points.append(f"Ask about: {persona['hobbies'][0]}")
        
        if persona['goals']:
            action_points.append(f"Discuss goals: {persona['goals'][0]}")
        
        # Communication approach
        action_points.append(f"Use {persona['preferences']['communication_style']} communication")
        
        return action_points
    
    def render_interface(self):
        """Render the Streamlit interface for persona search"""
        st.header("🔍 Natural Language Persona Search")
        st.markdown("Find compatible people using natural language queries with AI-powered matching.")
        
        # Search query
        st.subheader("💬 Search Query")
        query = st.text_area(
            "Describe what you're looking for:",
            placeholder="e.g., 'I want to find people with interests in AI and physics, and who love to play tennis. I don't want to see smokers.'",
            height=100,
            help="Use natural language to describe your search criteria"
        )
        
        # Preferences section
        st.subheader("⚙️ Search Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Interests
            interests_input = st.text_input(
                "Interests (comma-separated):",
                placeholder="AI, tennis, physics",
                help="Specific interests you want to match"
            )
            
            # Values
            values_input = st.text_input(
                "Values (comma-separated):",
                placeholder="innovation, collaboration, learning",
                help="Core values that matter to you"
            )
            
            # Location preference
            location_pref = st.text_input(
                "Location preference:",
                placeholder="New York, NY",
                help="Preferred location for connections"
            )
        
        with col2:
            # Age range
            age_range = st.slider(
                "Age range:",
                min_value=18,
                max_value=80,
                value=(25, 40),
                help="Preferred age range for connections"
            )
            
            # Number of results
            num_results = st.slider(
                "Number of results:",
                min_value=1,
                max_value=10,
                value=5,
                help="How many matches to return"
            )
        
        # Exclusions
        st.subheader("❌ Exclusions")
        exclusions_input = st.text_input(
            "What to exclude (comma-separated):",
            placeholder="smoking, unethical behavior",
            help="Things you want to avoid in matches"
        )
        
        # Search button
        if st.button("🔍 Search for Matches", type="primary"):
            if query.strip():
                # Parse inputs
                interests = [i.strip() for i in interests_input.split(',') if i.strip()] if interests_input else []
                values = [v.strip() for v in values_input.split(',') if v.strip()] if values_input else []
                exclusions = [e.strip() for e in exclusions_input.split(',') if e.strip()] if exclusions_input else []
                
                preferences = {
                    'interests': interests,
                    'values': values,
                    'location': location_pref,
                    'age_range': age_range
                }
                
                # Perform search
                with st.spinner("Searching for compatible people..."):
                    results = self.search_personas(query, preferences, exclusions, num_results)
                
                if results:
                    st.success(f"Found {len(results)} compatible matches!")
                    
                    # Display results
                    for i, result in enumerate(results):
                        persona = result['persona']
                        compatibility = result['compatibility_score']
                        
                        with st.expander(f"#{i+1} {persona['name']} - {compatibility:.1%} Match"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Age:** {persona['age']} | **Location:** {persona['location']}")
                                st.write(f"**Occupation:** {persona['occupation']}")
                                st.write(f"**Interests:** {', '.join(persona['interests'][:5])}...")
                                st.write(f"**Values:** {', '.join(persona['values'])}")
                                st.write(f"**Personality:** {', '.join(persona['personality'])}")
                            
                            with col2:
                                st.metric("Compatibility", f"{compatibility:.1%}")
                                st.metric("Age", persona['age'])
                            
                            # Insights
                            st.write("**💡 Insights:**")
                            st.write(result['insights'])
                            
                            # Action points
                            st.write("**🎯 Action Points:**")
                            for action in result['action_points']:
                                st.write(f"• {action}")
                            
                            # Communication preferences
                            st.write("**💬 Communication:**")
                            st.write(f"Style: {persona['preferences']['communication_style']}")
                            st.write(f"Meeting preference: {persona['preferences']['meeting_preference']}")
                
                else:
                    st.warning("No matches found. Try adjusting your search criteria.")
            else:
                st.warning("Please enter a search query.")
        
        # Example queries
        with st.expander("💡 Example Queries"):
            st.markdown("""
            ### Try these example searches:
            
            **AI/ML Researchers:**
            - "I have just moved to NYC - help me find my kinds of people, interested in AI/ML research"
            
            **Tennis Players:**
            - "I want to find people with interests in AI and physics, and who love to play tennis. I don't want to see smokers"
            
            **Environmentalists:**
            - "Looking for people passionate about nature conservation, people who share my values"
            
            **Tech Professionals:**
            - "Find software engineers who love tennis and have an active lifestyle"
            
            **Researchers:**
            - "Connect with biomedical researchers interested in public health and tennis"
            """)
        
        # Sample personas preview
        with st.expander("👥 Sample Personas"):
            st.markdown("**Available personas in the database:**")
            for persona in self.personas[:5]:  # Show first 5
                st.write(f"• **{persona['name']}** ({persona['age']}) - {persona['occupation']} in {persona['location']}")

def main():
    """Main function to run the persona search"""
    search = PersonaSearch()
    search.render_interface()

if __name__ == "__main__":
    main()
