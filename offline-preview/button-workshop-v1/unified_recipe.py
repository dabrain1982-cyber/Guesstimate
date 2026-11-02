"""Validate imported component measurements, without executing source markup."""
from copy import deepcopy
import math
import re
from xml.etree import ElementTree
ElementTree.register_namespace('','http://www.w3.org/2000/svg')


def validate_base(value,error):
    if not isinstance(value,dict) or len(str(value))>18000:raise error('Die Buttonbausteine sind unvollständig oder zu groß.')
    for key in ('width','height','font_size'):
        number=value.get(key)
        if type(number) not in (int,float) or not math.isfinite(number) or not 0<number<=2000:raise error('Ungültige Maße des Ausgangsbuttons.')
    def walk(item,key=''):
        if isinstance(item,dict):
            for k,v in item.items():
                if not isinstance(k,str) or len(k)>40:raise error('Ungültiger Baustein.')
                walk(v,k)
        elif isinstance(item,list):
            if len(item)>64:raise error('Zu viele Bestandteile.')
            for v in item:walk(v,key)
        elif isinstance(item,str):
            if len(item)>6500:raise error('Der Bild- oder Textbaustein ist zu groß.')
            if key=='svg' and item:
                try:node=ElementTree.fromstring(item)
                except ElementTree.ParseError:raise error('Ungültiges Bildzeichen.')
                for el in node.iter():
                    if el.tag.split('}')[-1] not in ('svg','g','path','circle','rect','line','polyline','polygon','ellipse','title'):raise error('Dieses Bildzeichen enthält unbekannte Bestandteile.')
                    for attr,val in list(el.attrib.items()):
                        if attr not in ('viewBox','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','points','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','width','height','xmlns'):
                            del el.attrib[attr]
                        elif re.search(r'url\(|[<>;{}]|https?:|javascript:',val,re.I):raise error('Ungültiges Bildzeichen.')
                value['svg']=ElementTree.tostring(node,encoding='unicode')
            elif re.search(r'[<>;{}\\\x00-\x1f]|javascript:|expression\s*\(',item,re.I):raise error('Ungültiger Gestaltungswert.')
            for target in re.findall(r'url\([\s\x22\x27]*([^\x22\x27)]+)',item):
                if not target.startswith(('/shared/','/static/','/assets/','/conquest-source/')):raise error('Bilder müssen aus der lokalen Bibliothek stammen.')
            if key=='image' and item and not item.startswith(('/shared/','/static/','/assets/','/conquest-source/')):raise error('Unbekannte Bildquelle.')
        elif item is not None and (type(item) not in (int,float) or not math.isfinite(item)):raise error('Ungültiger Bausteinwert.')
    value=deepcopy(value);walk(value);return value
