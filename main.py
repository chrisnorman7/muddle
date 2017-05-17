"""The main entry point."""

if __name__ == '__main__':
    from default_argparse import parser
    parser.add_argument(
        'world',
        metavar='WORLD-FILE',
        nargs='?',
        help='The world file to load into the first window'
    )
    args = parser.parse_args()
    import logging
    logging.basicConfig(
        stream=args.log_file,
        level=args.log_level,
        format=args.log_format)
    import application
    logging.info(
        'Starting %s, version %s.',
        application.name,
        application.__version__
    )
    from twisted.internet import reactor
    application.reload_plugins()
    from muddle.gui.main_frame import MainFrame
    from threading import Thread
    Thread(target=reactor.run, args=[False]).start()
    frame = MainFrame(filename=args.world)
    application.app.MainLoop()
    reactor.callFromThread(reactor.stop)
    for window in application.windows:
        world = window.world
        if world.name:
            logging.info('Saving world %s.', world.name)
            world.save()
        else:
            logging.info('Not saving world %r.', world)
    logging.info('Done.')
