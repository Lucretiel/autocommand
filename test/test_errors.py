import autocommand
from pytest import raises

def test_annotation_error():
	with raises(autocommand.AnnotationError):
		@autocommand.autocommand
		def annotate(arg1: 1):
			pass


def test_kwarg_error():
	with raises(autocommand.KWArgError):
		@autocommand.autocommand
		def kwarg(**kwargs):
			pass
