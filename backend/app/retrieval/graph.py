import spacy
from typing import List, Dict, Any
from ..shared.neo4j_client import neo4j_client
import logging

logger = logging.getLogger(__name__)

# Load English NLP model for entity extraction
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Spacy model 'en_core_web_sm' not found. Will download on the fly (not recommended for production).")
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extracts organizations, people, and geopolitical entities from text using spaCy.
    Returns a list of dicts: {"text": "Apple", "type": "Organization"}
    """
    doc = nlp(text)
    entities = []
    
    # Map spacy labels to our graph labels
    label_map = {
        "ORG": "Organization",
        "PERSON": "Person",
        "GPE": "Country"  # Geopolitical Entity mapped to Country for simplicity
    }
    
    for ent in doc.ents:
        if ent.label_ in label_map:
            entities.append({
                "text": ent.text,
                "type": label_map[ent.label_]
            })
            
    return entities

def retrieve_graph_context(query: str, hops: int = 2) -> List[str]:
    """
    Extracts entities from the query, maps them to Neo4j nodes, 
    and performs a graph traversal to find relationships and context.
    Returns a list of relationship strings.
    """
    entities = extract_entities(query)
    context_strings = []
    
    if not entities:
        return []
        
    for entity in entities:
        # 1. Match the node in the graph
        cypher_match = f"""
        MATCH (n:{entity['type']})
        WHERE toLower(n.name) CONTAINS toLower($name)
        RETURN n LIMIT 1
        """
        match_result = neo4j_client.query(cypher_match, {"name": entity["text"]})
        
        if not match_result:
            continue
            
        node = match_result[0]['n']
        node_id = node.element_id
        
        # 2. Expand 1 or 2 hops from the matched node
        if hops == 1:
            cypher_expand = """
            MATCH (n)-[r]-(m) 
            WHERE elementId(n) = $node_id
            RETURN n.name as source, type(r) as relationship, m.name as target, labels(m)[0] as target_type
            LIMIT 10
            """
        else:
            cypher_expand = """
            MATCH (n)-[r]-(m)-[r2]-(p)
            WHERE elementId(n) = $node_id
            RETURN n.name as source, type(r) as rel1, m.name as intermediate, type(r2) as rel2, p.name as target
            LIMIT 10
            """
            
        expand_results = neo4j_client.query(cypher_expand, {"node_id": node_id})
        
        for res in expand_results:
            if hops == 1:
                context_strings.append(f"{res.get('source')} {res.get('relationship')} {res.get('target')} ({res.get('target_type')})")
            else:
                context_strings.append(f"{res.get('source')} {res.get('rel1')} {res.get('intermediate')} {res.get('rel2')} {res.get('target')}")
                
    return list(set(context_strings)) # deduplicate
