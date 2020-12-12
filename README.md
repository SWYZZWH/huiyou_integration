# huiyou_integration
huiyou 后端的集成测试项目，使用 python nose 集成测试框架

## 依赖
    python 3.7
    requirements.txt

## 用法
### linux 环境下运行

    .sh start.sh env=local
    或
    .sh start.sh env=online


### windows 下运行

使用git bash在项目根目录下运行

    ./start.sh


或者

    pip install -r requirements.txt


根据要测试的环境（本地或线上）在项目根目录下运行：


    nosetests test_local.py
    或
    nosetests test_online.py

## 一些说明
nose手册 https://nose.readthedocs.io/en/latest/usage.html

测试会持续一段时间，请耐心等待

通过的每个测试用例会输出一个'.'，未通过测试的用例会输出一个'F', 执行出错的用例会输出一个'E'，出错和未通过的用例会打印出日志和标准输出，可能还包括异常栈方便排查

如果所有用例在本地均通过就可以上线了

增加测试用例只需要在test_local.py和test_online.py文件的主类中添加一个test开头的函数即可



