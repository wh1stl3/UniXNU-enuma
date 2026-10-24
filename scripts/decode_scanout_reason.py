"""Strict paired timing decoder, not a numeric register or frequency decoder."""
import math
LABELS=('strict_pattern','border_only','other_or_unknown_staging','dim_present','alpha_pattern_deviation','inherited_gate_or_instability')
def decode_pair(control,forward,reverse):
 if not all(isinstance(t,(int,float)) and not isinstance(t,bool) and math.isfinite(t) and t>0 for t in (control,forward,reverse)):
  return {'accepted':False,'reason':'invalid timing'}
 number=round((forward-reverse+20)/8)
 if not 0<=number<=5:return {'accepted':False,'reason':'outside class range'}
 difference_residual=forward-reverse-(8*number-20)
 f_residual=forward-control-4*number;r_residual=reverse-control-4*(5-number)
 sum_residual=forward+reverse-2*control-20
 accepted=abs(difference_residual)<=2 and abs(f_residual)<=2 and abs(r_residual)<=2 and abs(sum_residual)<=3
 return dict(accepted=accepted,class_number=number if accepted else None,class_label=LABELS[number] if accepted else None,nearest_class=number,difference_residual=round(difference_residual,3),forward_baseline_residual=round(f_residual,3),reverse_baseline_residual=round(r_residual,3),paired_sum_residual=round(sum_residual,3))
