
class JELPrettyPrint(object):
	@staticmethod
	def pretty_print_error(error, should_print_errors_to_stderr=False):
		theError = '\033[91m' + error + '\033[0m'
		if should_print_errors_to_stderr:
			print >> sys.stderr, theError
		else:
			print theError

	@staticmethod
	def pretty_print_positive(output):
		print '\033[92m' + output + '\033[0m'

	@staticmethod
	def pretty_print(output):
		print '\033[95m' + output + '\033[0m'


    