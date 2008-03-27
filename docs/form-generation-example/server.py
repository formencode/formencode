import sys, os

# This sets up the path so we can import the other modules:
sys.path.insert(0, os.path.dirname(__file__))

from generatorapp import CrudApp

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser(
        usage='%prog --port=PORT BASE_DIRECTORY'
        )
    parser.add_option(
        '-p', '--port',
        default='8080',
        dest='port',
        type='int',
        help='Port to serve on (default 8080)')
    app = CrudApplication()
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', options.port, app)
    print 'Serving on http://localhost:%s' % options.port
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print '^C'
