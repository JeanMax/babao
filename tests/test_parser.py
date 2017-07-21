import babao.parser as pars


def test_parseArgv():
    args = pars.parseArgv("d")
    assert args.func
    assert not args.verbose
    assert not args.graph

    args = pars.parseArgv(["-v", "d"])
    assert args.verbose

    args = pars.parseArgv(["-g", "d"])
    assert args.graph

    args = pars.parseArgv(["-g", "-v", "d"])
    assert args.verbose
    assert args.graph
