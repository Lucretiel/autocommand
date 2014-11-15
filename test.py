from automain import automain

@automain(__name__, 'This is a test automain program')
def main(
      param1: (bool, 'This is param1'),
      param2: (bool, 'This is param2'),
      verbose: bool,
      quiet: bool,
      hostname,
      port=4747,
      *files: "The list of files to read from"):

    if quiet:
        print('Fuck you I talk as much as I want')
    if verbose:
        print('I am being verbose')
    print('param1:', param1)
    print('param2:', param2)

    print('Connecting to {}:{}'.format(hostname, port))
    print('Here are the files you requested:')
    for f in files:
        print(f)
