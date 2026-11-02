"""Missing whole quiz windows, captured from the existing templates with neutral fixtures."""
from source_windows import SourceWindows,Fragments


def definitions():
    rows=[]
    for game,template in [('Guesstimate','question.html'),('Guesstimate Party','party_question.html')]:
        for category,label in [('true_false','Wahr / Falsch'),('multiple_choice','Auswahl'),('match','Zuordnen'),('order','Reihenfolge'),('estimate','Schätzen')]:
            rows.append(dict(model='quiz-question-card',family='actions',title='Vollständiges Fragenfenster',template=template,target={'class':'question-card'},game=game,state=label,values=dict(workshop_category=category,feedback=None),preview_size=(1120,1200)))
        for credit,label in [(1,'Richtig'),(.5,'Teilweise richtig'),(0,'Falsch')]:
            rows.append(dict(model='quiz-question-card',family='actions',title='Vollständiges Fragenfenster',template=template,target={'class':'question-card'},game=game,state='Auflösung · '+label,values=dict(workshop_credit=credit),preview_size=(1120,1200)))
    for score in (100,320,500):
        rows.append(dict(model='quiz-result-window',family='actions',title='Vollständiges Rundenergebnis',template='result.html',target={'class':'result-hero'},game='Guesstimate',state=str(score)+' Punkte',values=dict(workshop_score=score),preview_size=(1120,1200)))
    for credit,label in [(1,'Richtig'),(.5,'Teilweise richtig'),(0,'Falsch')]:
        rows.append(dict(model='quiz-answer-review',family='actions',title='Antwortübersicht der Runde',template='result.html',target={'class':'answer-review'},game='Guesstimate',state=label,values=dict(workshop_credit=credit),preview_size=(1120,1000)))
    for tab,label in [('daily','Tag'),('weekly','Woche'),('all','Hall of Fame'),('weekly_wins','Wochensiege')]:
        rows.append(dict(model='quiz-ranking-window',family='actions',title='Vollständiger Ranglistenrahmen',template='home.html',target={'data-leaderboards':None},game='Guesstimate',state=label,values=dict(workshop_ranking_tab=tab),source='templates/_leaderboard.html',source_target={'class':'variant-a-leaderboard'},preview_root_width=620,preview_size=(800,1200)))
    for tab,label in [('daily','Tag'),('weekly','Woche'),('all','Hall of Fame')]:
        rows.append(dict(model='quiz-ranking-window',family='actions',title='Vollständiger Ranglistenrahmen',template='result.html',target={'data-leaderboards':None},game='Guesstimate',state='Ergebnisseite · '+label,values=dict(workshop_ranking_tab=tab,workshop_ranking_layout='result'),source='templates/_leaderboard.html',preview_root_width=800,preview_size=(960,1200)))
    rows.append(dict(model='quiz-empty-pool',family='actions',title='Hinweis bei leerem Fragenvorrat',template='pool_exhausted.html',target={'class':'party-head'},game='Guesstimate',state='Neutraler Leerzustand',preview_size=(960,720)))
    return rows


class CompletionLibrary(SourceWindows):
    identifier_prefix='source-completion-'
    api_prefix='/api/completion-windows/'
    model_names={'quiz-question-card':'Quiz · vollständiges Fragenfenster','quiz-result-window':'Quiz · vollständiges Ergebnisfenster','quiz-empty-pool':'Quiz · Leerzustandsfenster','quiz-answer-review':'Quiz · Antwortübersicht','quiz-ranking-window':'Quiz · Ranglistenrahmen'}

    def __init__(self,buttons):super().__init__(buttons,definitions_list=definitions())

    def fragment(self,text,definition,original=False):
        if original and definition.get('values',{}).get('workshop_ranking_layout')=='result':
            return next(row for row in Fragments(text).elements if 'data-leaderboards' in row['attrs'] and 'variant-a-leaderboard' not in row['attrs'].get('class',''))
        return super().fragment(text,definition,original)

    def context(self,definition):
        values=super().context(definition)
        values['timer_decay']=values['timer_limit']-values['timer_hold']
        if values.get('feedback'):
            values['feedback']['points']=int(100*values['feedback']['credit'])
        if definition['model']=='quiz-result-window':
            values['attempt']=dict(score=definition['values']['workshop_score'])
        if definition['model']=='quiz-ranking-window':
            values['leaderboards']={key:[dict(player,rank=i+1,rounds=5) for i,player in enumerate(values['players'])] for key in values['leaderboards']}
        if definition['model']=='quiz-answer-review':
            credit=definition['values']['workshop_credit']
            values['answer_review']=[dict(credit=credit,category_label='Beispiel',knowledge_category_label='',points=int(100*credit),
                question=values['question'],submitted='Beispielantwort' if credit==1 else 'Andere Beispielantwort',correct_answer='Beispielantwort',order_correct_count=None,accuracy_points=int(100*credit),response_seconds=1.5)]
        return values

    def decorate(self,definition,rendered):
        if definition['model']!='quiz-ranking-window':return rendered
        markup=rendered['markup'];tab=definition['values']['workshop_ranking_tab']
        for row in Fragments(markup).elements:
            attrs=row['attrs'];original=row['markup']
            if 'data-leaderboard-tab' in attrs:
                markup=markup.replace(original,original.replace('aria-selected="'+attrs['aria-selected']+'"','aria-selected="'+str(attrs['data-leaderboard-tab']==tab).lower()+'"'))
            if 'data-leaderboard-panel' in attrs:
                opening,rest=original.split('>',1);opening=opening.replace(' hidden','')
                if attrs['data-leaderboard-panel']!=tab:opening+=' hidden'
                markup=markup.replace(original,opening+'>'+rest)
        rendered['markup']=markup;return rendered
