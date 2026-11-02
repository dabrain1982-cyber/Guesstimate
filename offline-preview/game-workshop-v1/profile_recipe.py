"""Map source measurements into the existing workshop's shared recipe fields."""
from copy import deepcopy


def from_profile(profile,source,catalog):
    p=deepcopy(profile)
    s={**catalog['defaults'],**dict(style='minimal',material=p['material'],shape='custom',edge=min(5,round(p['edge'])),finish='matte',wear=0,
        accent=p['accent'],gradient_to=p['gradient_to'],opacity=round(p['opacity']/5)*5,font='source',font_link='manual',lettering='plain',
        label=p['text'],depth=max(0,min(20,round(p['depth']['y']))),depth_x=max(-20,min(20,round(p['depth']['x']))),depth_mode='manual',
        depth_color=p['depth']['color'],ink_mode='manual',ink_color=p['ink'],font_scale=100,shadow=0 if p['soft_shadow']=='none' else 25,sound='off')}
    p['initial']={key:s[key] for key in ('material','accent','gradient_to','opacity','shadow')}
    return dict(schema_version=4,kind='button',name=source['name'][:80],notes='Eigener Entwurf aus '+source['name'],parent_id=None,
                settings=s,contour=deepcopy(p['contour']),base=p,source_button=deepcopy(source),review={key:'open' for key,_ in catalog['review_dimensions']})
