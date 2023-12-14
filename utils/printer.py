import sys

def msg(message, origin):
    print("\n (%s): %s " % (origin, message))

def err(message, origin):
    print("\n ERROR (%s): %s " % (origin, message), file=sys.stderr)