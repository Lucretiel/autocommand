from unittest.mock import patch
import pytest
from autocommand import autocommand


@pytest.mark.parametrize('module_name', [
	'__main__',
	True])
def test_name_main(capsys, module_name):
	try:
		with patch('sys.argv', ['prog', 'foo', 'bar']):
			@autocommand(module_name)
			def prog(arg1, arg2):
				print(arg1, arg2)
				return 10

	except SystemExit as e:
		assert e.code == 10
	else:
		pytest.fail('autocommand function failed to raise SystemExit')

	out, err = capsys.readouterr()
	assert out == "foo bar\n"
