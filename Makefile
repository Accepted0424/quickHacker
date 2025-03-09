# 定义 Python 环境
PYTHON=python
PIP=pip

DIRECTORY = ./
KEEP_FILES = main.py requirements.txt Makefile test.py dataMaker utils

# 定义项目中的文件
REQUIREMENTS=requirements.txt
MAIN_FILE=main.py

# 默认目标，运行程序
run: install
	$(PYTHON) $(MAIN_FILE)

# 安装所有依赖
install:
	$(PIP) install -r $(REQUIREMENTS)

# 目标：清空目录
clean:
	@echo "Cleaning directory $(DIRECTORY), keeping files: $(KEEP_FILES)"
	# 删除目录下除指定文件和文件夹外的所有文件
	@find $(DIRECTORY) -type f ! -name $(foreach file,$(KEEP_FILES),-not -name $(file)) -exec rm -f {} +
	@find $(DIRECTORY) -type d ! -name $(foreach folder,$(KEEP_FILES),-not -name $(folder)) -exec rm -rf {} +
