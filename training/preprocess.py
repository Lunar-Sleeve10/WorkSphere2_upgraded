import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
import pandas as pd
import json
import logging
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='pandas')


def convert_resume_dataset(nlp, filepath):
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
                        if label_name == 'Skills': entity_label = 'SKILL'
                        elif label_name == 'Name': entity_label = 'PERSON'
                        if entity_label:
                            span = doc.char_span(start, end + 1, label=entity_label, alignment_mode="contract")
                            if span is not None: spans.append(span)
                doc.ents = filter_spans(spans)
                if doc.ents: db.add(doc)
        return db
    except Exception as e:
        logging.exception(f"Unable to process resume dataset: {e}")
        return None

def convert_general_ner_dataset(nlp, filepath):
    db = DocBin()
    try:
        data = pd.read_csv(filepath, encoding="latin1").ffill()
        grouped = data.groupby("Sentence #", group_keys=False).apply(
            lambda s: [(w, t) for w, t in zip(s["Word"].values.tolist(), s["Tag"].values.tolist())]
        )
        for sentence in grouped:
            text = " ".join([word for word, tag in sentence])
            doc = nlp.make_doc(text)
            spans = []
            current_pos = 0
            for i, (word, tag) in enumerate(sentence):
                start_char = text.find(word, current_pos)
                if start_char == -1: continue
                end_char = start_char + len(word)
                current_pos = end_char + 1
                if tag == 'B-per':
                    j = i + 1
                    while j < len(sentence) and sentence[j][1] == 'I-per':
                        next_word_start = text.find(sentence[j][0], end_char)
                        if next_word_start == -1: break
                        end_char = next_word_start + len(sentence[j][0])
                        j += 1
                    span = doc.char_span(start_char, end_char, label="PERSON")
                    if span is not None: spans.append(span)
            doc.ents = filter_spans(spans)
            if doc.ents: db.add(doc)
        return db
    except Exception as e:
        logging.exception(f"Unable to process general NER dataset: {e}")
        return None

# --- Main pre-processing logic ---
def create_training_data():
    nlp = spacy.blank("en")
    resume_json_path = 'Entity Recognition in Resumes.json'
    general_csv_path = 'ner_dataset.csv'
    output_path = 'train.spacy'

    print("--- Starting Data Pre-processing ---")
    
    print(f"\nProcessing resume dataset from '{resume_json_path}'...")
    db_resumes = convert_resume_dataset(nlp, resume_json_path)
    print(f"Found {len(db_resumes)} documents in resume dataset.")

    print(f"\nProcessing general NER dataset from '{general_csv_path}'...")
    db_general = convert_general_ner_dataset(nlp, general_csv_path)
    print(f"Found {len(db_general)} documents in general dataset.")

    # Combine the DocBin objects
    combined_db = DocBin()
    for doc in db_resumes.get_docs(nlp.vocab):
        combined_db.add(doc)
    for doc in db_general.get_docs(nlp.vocab):
        combined_db.add(doc)
        
    combined_db.to_disk(output_path)
    print(f"\n Success! Combined data and saved {len(combined_db)} documents to '{output_path}'.")
    print("You can now run the training script.")

if __name__ == '__main__':
    create_training_data()