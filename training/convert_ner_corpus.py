import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans, minibatch, compounding
from spacy.training.example import Example

import json
import pandas as pd
import logging
import random
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='pandas')


def convert_resume_dataset(filepath):
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
                filtered_spans = filter_spans(spans)
                doc.ents = filtered_spans
                if doc.ents:
                    db.add(doc)
        return db
    except Exception as e:
        logging.exception(f"Unable to process resume dataset: {e}")
        return None

def convert_general_ner_dataset(filepath):
    nlp = spacy.blank("en")
    db = DocBin()
    try:
        data = pd.read_csv(filepath, encoding="latin1")
        data = data.ffill()
        agg_func = lambda s: [(w, t) for w, t in zip(s["Word"].values.tolist(), s["Tag"].values.tolist())]
        grouped = data.groupby("Sentence #", group_keys=False).apply(agg_func)
        sentences = [s for s in grouped]
        for sentence in sentences:
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
                    span = doc.char_span(start_char, end_char, label="PERSON")
                    if span is not None:
                        j = i + 1
                        while j < len(sentence) and sentence[j][1] == 'I-per':
                            next_word_start = text.find(sentence[j][0], end_char)
                            if next_word_start == -1: break
                            end_char = next_word_start + len(sentence[j][0])
                            j += 1
                        full_span = doc.char_span(span.start_char, end_char, label="PERSON")
                        if full_span is not None:
                            spans.append(full_span)
            filtered_spans = filter_spans(spans)
            doc.ents = filtered_spans
            if doc.ents:
                db.add(doc)
        return db
    except Exception as e:
        logging.exception(f"Unable to process general NER dataset: {e}")
        return None

def train_unified_model():
   
    if spacy.prefer_gpu():
        print(" Successfully enabled GPU. Training on NVIDIA GPU.")
    else:
        print(" Could not enable GPU. Training on CPU.")


    resume_json_path = 'Entity Recognition in Resumes.json'
    general_csv_path = 'ner_dataset.csv'
    output_dir = Path.cwd() / 'custom_ner_model'

    print("\nLoading and converting resume dataset...")
    doc_bin_resumes = convert_resume_dataset(resume_json_path)
    
    print("Loading and converting general NER dataset...")
    doc_bin_general = convert_general_ner_dataset(general_csv_path)

    if not doc_bin_resumes or not doc_bin_general:
        print("Failed to load one or both datasets. Exiting.")
        return
        
    nlp_vocab = spacy.blank("en").vocab
    docs_resumes = list(doc_bin_resumes.get_docs(nlp_vocab))
    docs_general = list(doc_bin_general.get_docs(nlp_vocab))
    docs = docs_resumes + docs_general
    
    print(f"Total training examples from resumes: {len(docs_resumes)}")
    print(f"Total training examples from general corpus: {len(docs_general)}")
    print(f"Total combined training examples: {len(docs)}")
    
    if not docs:
        print("No training data found. Exiting.")
        return


    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner", last=True)
    ner.add_label("SKILL")
    ner.add_label("PERSON")

   
    print("\nStarting unified model training with batching...")
    optimizer = nlp.begin_training()

    for iteration in range(30):
        random.shuffle(docs)
        losses = {}
        
        batches = minibatch(docs, size=256)
        
        for batch in batches:
            examples = []
            for doc in batch:
                entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
                example = Example.from_dict(doc, {"entities": entities})
                examples.append(example)

            if examples:
                nlp.update(examples, sgd=optimizer, losses=losses, drop=0.35)
        
        print(f"Iteration {iteration}, Losses: {losses}")

   
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        
    nlp.to_disk(output_dir)
    print(f"\nUnified custom model saved to '{output_dir}' directory.")



if __name__ == '__main__':
    train_unified_model()