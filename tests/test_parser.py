import babao.arg as arg


def test_parseArgv():
    args = arg.parseArgv("d")
    assert args.func
    assert args.verbose == 1
    assert not args.quiet
    assert not args.graph

    args = arg.parseArgv(["-v", "d"])
    assert args.verbose == 2

    args = arg.parseArgv(["-vv", "d"])
    assert args.verbose == 3

    args = arg.parseArgv(["-q", "d"])
    assert args.quiet

    args = arg.parseArgv(["-g", "d"])
    assert args.graph

    args = arg.parseArgv(["-g", "-v", "d"])
    assert args.verbose == 2
    assert args.graph
