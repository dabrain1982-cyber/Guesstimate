// One selected front set for every live Blackjack hand and flying card.
export const frontSetId='ivory-v1-large-index';
export const frontPattern=new URL('./cards/blackjack/fronts-ivory-v1/__CARD__.svg?v=3',import.meta.url).href;
export const frontUrl=code=>frontPattern.replace('__CARD__',code);
