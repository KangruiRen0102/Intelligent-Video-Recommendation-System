import os
import shutil

if __name__ == '__main__':
	my_path = os.path.abspath(os.path.dirname(__file__))
	src = os.path.join(my_path, '../checkpoint/model')
	dst = os.path.join(my_path, '../checkpoint/baseline_model')
	if os.path.isdir(dst):
		shutil.rmtree(dst)
	shutil.copytree(src, dst)
