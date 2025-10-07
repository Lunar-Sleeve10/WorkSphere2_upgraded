import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

import json
import logging

from pathlib import Path

def convert_resume_dataset(filepath):
    """
    Converts the "Resume Entities for NER" JSON dataset.
    Extracts 'Skills' as SKILL and 'Name' as PERSON entities.
    """
    nlp = spacy.blank("en")
    db = DocBin()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            
            if data['annotation'] is not None:
                doc = nlp.make_doc(text)
                spans = []
                for annotation in data['annotation']:
                    if annotation['label']:
                        label_name = annotation['label'][0]
                        point = annotation['points'][0]
                        start, end = point['start'], point['end']
                        
                        entity_label = ""
                        if label_name == 'Skills':
                            entity_label = 'SKILL'
                        elif label_name == 'Name':
                            entity_label = 'PERSON'

                        if entity_label:
                            span = doc.char_span(start, end + 1, label=entity_label, alignment_mode="contract")
                            if span is not None:
                                spans.append(span)
                
                # Filter out any overlapping entities
                filtered_spans = filter_spans(spans)
                doc.ents = filtered_spans
                
                if doc.ents:
                    db.add(doc)
                    
        return db
    except Exception as e:
        logging.exception(f"Unable to process resume dataset: {e}")
        return None