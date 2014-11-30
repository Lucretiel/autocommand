from automain import automain

@automain(__name__, 'This is a test automain program')
def main(
      hostname,
      param1=False,
      param2=False,
      verbose=False,
      quiet=False,
      config: 'Config file to load from. Defaults to ~/.testrc' ='~/.testrc',
      port=4747,
      *files: "The list of files to read from"):

    if quiet:
        print('Fuck you I talk as much as I want')
    if verbose:
        print('I am being verbose')

    print('Loaded config from {}'.format(config))
    print('param1:', param1)
    print('param2:', param2)

    print('Connecting to {}:{}'.format(hostname, port))
    print('Here are the files you requested:')
    for f in files:
        print(f)
