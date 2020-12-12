# 启动脚本 for linux
pip install -r requirements.txt

if [$1 == "online"]
then
    nosetests test_online.py 
elif [$1 == "local"]
then
    nosetests test_local.py
else
    echo "Environment $1 dose not exist!"
fi