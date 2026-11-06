"""Explicit crypto startup ownership for the platform link only."""
def platform_environment(base, features, mode):
    if mode not in ('source', 'prelinked'):
        raise ValueError('Unknown crypto bootstrap mode')
    result = dict(base)
    result.update(features)
    if result.get('XNU_SOURCE_CORECRYPTO14') != '1':
        raise ValueError('Platform crypto archives must remain enabled')
    result['XNU_CRYPTO_BOOTSTRAP'] = mode
    return result


def audit(mode, arguments, symbols):
    """Check effective ordered macro options, not just the requested setting."""
    if mode not in ('source', 'prelinked') or not isinstance(arguments, list):
        raise ValueError('Invalid crypto audit input')
    defined = None
    iterator = iter(arguments)
    for arg in iterator:
        if not isinstance(arg, str):
            raise ValueError('Compiler arguments must be strings')
        if arg in ('-D', '-U'):
            arg += next(iterator, '')
        if arg.startswith(('-D', '-U')) and arg[2:].split('=', 1)[0] == 'XNU_SOURCE_CORECRYPTO14':
            defined = arg.startswith('-D')
    startup = '_source_corecrypto14_bootstrap' in symbols
    expected = mode == 'source'
    if defined is not expected or startup != expected:
        raise ValueError('Crypto startup mode disagrees with final compiler record or kernel symbols')
    if '_register_and_init_prng' not in symbols:
        raise ValueError('Kernel PRNG registration function missing')
    return dict(mode=mode,source_macro_defined=defined,source_startup_present=startup,
                registration_present=True,passed=True,donor_runtime_verified=False)
