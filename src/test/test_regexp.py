import regexp


def test_wildcard():
    assert regexp.match('.', 'a')
    assert regexp.match('.', '8')
    assert regexp.match('.', '\t')
    assert not regexp.match('.', '')


def test_escaped():
    assert regexp.match('\\.', '.')
    assert regexp.match('\\\\', '\\')
    assert regexp.match('\\.', '.')
    assert regexp.match('\\t', '\t')
    assert not regexp.match('\\\\n', '\n')
    assert not regexp.match('\\.', 'a')


def test_charclass():
    assert regexp.match('[a-zA-Z0-9]', 'a')
    assert regexp.match('[a-zA-Z0-9]', 'A')
    assert regexp.match('[a-zA-Z0-9]', '0')
    assert not regexp.match('[a-zA-Z0-9]', '.')

    assert regexp.match('[abc]', 'a')
    assert not regexp.match('[abc]', 'd')
    assert not regexp.match('[.]', 'a')


def test_charclass_complement():
    assert not regexp.match('[^a-zA-Z0-9]', 'a')
    assert not regexp.match('[^a-zA-Z0-9]', 'A')
    assert not regexp.match('[^a-zA-Z0-9]', '0')
    assert regexp.match('[^a-zA-Z0-9]', '.')

    assert not regexp.match('[^abc]', 'a')
    assert regexp.match('[^abc]', 'd')
    assert regexp.match('[^.]', 'a')


def test_star():
    assert regexp.match('^a*$', '')
    assert regexp.match('^a*$', 'aaaaaaaa')
    assert regexp.match('^(foo)*$', 'foofoofoo')
    assert not regexp.match('^a*$', 'bbbb')


def test_plus():
    assert regexp.match('^a+$', 'aaaaaaaa')
    assert regexp.match('^(foo)+$', 'foofoofoo')
    assert not regexp.match('^a+$', '')
    assert not regexp.match('^a+$', 'bbbb')


def test_optional():
    assert regexp.match('^(foo)?$', '')
    assert regexp.match('^foo?$', 'fo')


def test_concatenation():
    assert regexp.match('^a+b+$', 'aaabbb')
    assert not regexp.match('^a+b+$', 'abab')
    assert not regexp.match('^a+b+$', 'aaaa')


def test_union():
    assert regexp.match('^foo|bar$', 'bar')
    assert not regexp.match('^foo|bar$', 'foobar')


def test_repetition():
    assert regexp.match('^(ab){5}$', 'ab' * 5)
    assert not regexp.match('^(ab){5}$', 'ab' * 4)
    assert not regexp.match('^(ab){5}$', 'ab' * 6)

    assert regexp.match('^(ab){5,}$', 'ab' * 5)
    assert regexp.match('^(ab){5,}$', 'ab' * 6)
    assert not regexp.match('^(ab){5,}$', 'ab' * 4)

    assert regexp.match('^(ab){,5}$', 'ab' * 5)
    assert regexp.match('^(ab){,5}$', 'ab' * 4)
    assert not regexp.match('^(ab){,5}$', 'ab' * 6)

    assert regexp.match('^(ab){4,5}$', 'ab' * 4)
    assert regexp.match('^(ab){4,5}$', 'ab' * 5)
    assert not regexp.match('^(ab){4,5}$', 'ab' * 3)
    assert not regexp.match('^(ab){4,5}$', 'ab' * 6)


def test_begin_token():
    assert regexp.match('^foo', 'foobar')
    assert regexp.match('bar', 'foobar')
    assert not regexp.match('^bar', 'foobar')


def test_end_token():
    assert regexp.match('bar$', 'foobar')
    assert regexp.match('foo', 'foobar')
    assert not regexp.match('foo$', 'foobar')
