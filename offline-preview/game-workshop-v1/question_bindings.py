"""Question windows link to growing banks by field contract, never by question ID."""
from copy import deepcopy
import json
from library_store import ROOT


def binding_for(asset):
    if asset.get('source') != 'game' or asset['kind'] != 'windows':
        return None
    model = asset.get('model_id')
    if model == 'window-perfect-card':
        target = asset['snapshot'].get('source', {}).get('target', {}).get('class', '')
        if target not in ('perfect-question-card', 'perfect-points-card', 'perfect-vote-card', 'perfect-review-card'):
            return None
        sources = [dict(type=kind, label=label, path='fragen/stormseedsperfekt/'+folder+'/fragen.json')
                   for kind, label, folder in [('term', 'Begriffe', 'begriffe'), ('curiosity', 'Kuriositäten', 'kuriositaeten')]]
        loader = 'nerd_mode.py'
    elif model in ('window-quiz-answer-form', 'window-quiz-feedback', 'window-quiz-question-card', 'window-quiz-answer-review'):
        manifest = json.loads((ROOT/'fragen/manifest.json').read_text(encoding='utf-8'))
        sources = [dict(type=kind, label=meta['label'], path='fragen/'+meta['directory']+'/fragen.json')
                   for kind, meta in manifest['question_types'].items() if meta['active']]
        loader = 'questions.py'
    else:
        return None
    return dict(schema=1, kind='question_bank_reference', contract='fragen/STECKBRIEF.md', loader=loader,
                sources=sources, fields=['id', 'prompt', 'answer', 'source'],
                type_fields=({'term': ['card_type', 'term'], 'curiosity': ['card_type', 'explanation']}
                             if loader == 'nerd_mode.py' else
                             {'common': ['question_type', 'explanation', 'subject_keys'],
                              'multiple_choice': ['options'], 'true_false': [], 'match': ['left', 'right'],
                              'order': ['items'], 'estimate': ['unit']}),
                preview='Neutraler Platzhalter aus der bestehenden Fensterkomponente',
                growth='Neue Fragen verändern weder Bausteinzahl noch Bausteinkennungen.')


def annotate_assets(assets):
    """Only annotate generated catalog copies; private snapshots stay exact."""
    for asset in assets:
        if asset.get('source') in ('saved', 'legacy'):
            continue
        if asset.get('source') == 'game':
            asset['record_role'] = 'component_example'
        elif asset.get('source') == 'existing' or asset.get('image'):
            asset['record_role'] = 'finite_artwork'
        else:
            asset.setdefault('record_role', 'component')
        binding = binding_for(asset)
        if binding:
            asset['snapshot']['data_binding'] = deepcopy(binding)
        if asset.get('model_id') == 'window-perfect-card':
            asset['model_name'] = 'Perfect · Fragenfenster'
        snapshot = asset.get('snapshot', {})
        if (snapshot.get('content', {}).get('kind') == 'question'
                or snapshot.get('original_content', {}).get('card_type') in ('term', 'curiosity')):
            raise ValueError('Einzelne Fragen dürfen keine automatisch erzeugten Werkstattbausteine sein.')
    return assets
