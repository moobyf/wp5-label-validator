"""
Configuration settings for Label Validator.
"""
import os
import json

DEFAULT_LABELS = [
    'Abudefduf_vaigiensis', 'Aluterus_monoceros', 'Aluterus_scripta', 'Cantherhines_pardalis', 'Canthidermis_maculatus', 'Caranx_sexfasciatus', 'Carcharhinus_falciformis', 'Carcharhinus_longimanus', 'Coryphaena_hippurus', 'Decapterus_macarellus', 'Diver', 'Elagatis_bipinnulata', 'Fish', 'Kyphosus_vaigiensis', 'Meiacanthus_grammistes', 'Naucrates_ductor', 'Platax_teira', 'Seriola_rivoliana', 'Shark', 'Terapon_theraps', 'Thunnus_albacares', 'not_fish'
]

INITIAL_LABELS = DEFAULT_LABELS.copy()
SHUTDOWN_TIMEOUT = 3600
HEARTBEAT_INTERVAL = 60
LABELS_FILE = os.path.expanduser('~/.dash_validator_labels.json')


def load_labels_from_file():
    try:
        if os.path.exists(LABELS_FILE):
            with open(LABELS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Could not load labels: {e}")
    return DEFAULT_LABELS.copy()


def save_labels_to_file(labels):
    try:
        with open(LABELS_FILE, 'w') as f:
            json.dump(labels, f)
    except Exception as e:
        print(f"Could not save labels: {e}")
