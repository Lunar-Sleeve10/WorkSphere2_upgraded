import spacy
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
from pathlib import Path

def train_spacy_model():
    """Loads pre-processed data and trains the NER model."""
    
    # --- 1. Load Pre-processed Data ---
    training_data_file = 'train.spacy'
    output_dir = Path.cwd() / 'custom_ner_model'
    
    if not Path(training_data_file).exists():
        print(f"Error: Training data file not found: '{training_data_file}'")
        print("Please run the 'preprocess.py' script first to create it.")
        return

    # Check for GPU and prefer it
    if spacy.prefer_gpu():
        print("✅ Successfully enabled GPU. Training on NVIDIA GPU.")
    else:
        print("⚠️ Could not enable GPU. Training on CPU.")

    # --- 2. Setup Model ---
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner", last=True)
    # Add labels that you know are in your data
    ner.add_label("SKILL")
    ner.add_label("PERSON")

    # --- 3. Train Model ---
    print("\n--- Starting Model Training ---")
    optimizer = nlp.begin_training()

    # Load the DocBin from the pre-processed file
    db = DocBin().from_disk(training_data_file)
    docs = list(db.get_docs(nlp.vocab))
    print(f"Loaded {len(docs)} training examples.")

    for iteration in range(60):
        random.shuffle(docs)
        losses = {}
        
        # Use a large, fixed batch size for best performance
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

    # --- 4. Save Model ---
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    nlp.to_disk(output_dir)
    print(f"\n✅ Training complete! Model saved to '{output_dir}'.")


if __name__ == '__main__':
    train_spacy_model()