"""Reuse independent resource-class inventory for the exact1024 job."""
import trellis301_verify_cleanup as verify
import trellis301_cascade as cascade

if __name__=='__main__':
    verify.m=cascade
    verify.main()
