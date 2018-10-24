import os
import sys

def merge(directory):
	#根据ts片段持久化时的命名规则，找到头和尾（可以删掉头部、尾部的几个ts片段）
	numbers=[int(file_name.split('.')[0]) for file_name in os.listdir(directory)]
	start=min(numbers)
	end=max(numbers)+1
	#合并ts片段，存为与文件夹同名的ts文件
	with open(f'{directory}.ts','wb') as f:
		for n in range(start,end):
			file_path=os.path.join(directory,f'{n}.ts')
			with open(file_path,'rb') as g:
				f.write(g.read())

if __name__=='__main__':
	merge(sys.argv[1])#片段所在文件夹名作为命令行参数