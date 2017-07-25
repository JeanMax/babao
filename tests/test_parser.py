import babao.parser as pars


def test_parseArgv():
    args = pars.parseArgv("d")
    assert args.func
    assert args.verbose == 1
    assert not args.quiet
    assert not args.graph

    args = pars.parseArgv(["-v", "d"])
    assert args.verbose == 2

    args = pars.parseArgv(["-vv", "d"])
    assert args.verbose == 3

    args = pars.parseArgv(["-q", "d"])
    assert args.quiet

    args = pars.parseArgv(["-g", "d"])
    assert args.graph

    args = pars.parseArgv(["-g", "-v", "d"])
    assert args.verbose == 2
    assert args.graph
