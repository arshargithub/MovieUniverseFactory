"""Use the existing exact-frame/decode review for the new offline edit."""
from pathlib import Path
import entrance189_edit_review as review

if __name__=='__main__':
    review.OUT=Path(__file__).resolve().parents[1]/'.runtime/art-direction/series01-trailer-edit190'
    review.main()
