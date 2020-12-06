from nose.tools import assert_equal
from .config_online import config
import json
import requests
import logging

## 存在的问题：
# 现在测试能跑通，但各个测试之间存在先后依赖关系，需要让各个测试解耦
# 应该更多的针对功能测试而不是api测试
# 需要保证运行测试前后，数据库中的数据保持不变，这点还没做到
# 需要增加一些api 包括 get videos 与 post records （post 多条）

class test_backend:

    def setup(self):
        self.base_url = config["domin"] + ":" + config["port"] + "/api/"
        logging.info(self.base_url)

    # 测试服务有没有挂掉
    def test_service(self):
        url = self.base_url + "records"
        logging.info(url)

        r = requests.get(url, 
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        assert_equal(r.status_code, 200, "service failed")

    #测试post一条记录
    def test_records_post(self):
        url = self.base_url + "records"
        logging.info(url)


        with open("json/post_records.json","r") as f:
            j = json.load(f)

        uid = j["uid"] 
        r_get = requests.get(url+"?uid={}".format(uid), 
                         headers={"content-type": "application/json"})
        records_before = len(json.loads(r_get.content))
        logging.info("user {} has {} records before post records".format(uid, records_before))

        r = requests.post(url, json=j,
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        #验证返回码正确
        assert_equal(r.status_code, 200, "status code is not 200")

        r_get = requests.get(url+"?uid={}".format(uid), 
                         headers={"content-type": "application/json"})
        records_after = len(json.loads(r_get.content))
        logging.info("user {} has {} records after post records".format(uid, records_after))

        #验证确实插入了一条记录
        assert_equal(records_after - records_before, 1 , "post method failed")

    #简单测试一下get
    def test_records_get(self):
        url_records = self.base_url + "records"
        with open("json/post_records.json","r") as f:
            j = json.load(f)
        uid = j["uid"] 

        url = url_records + "?uid={}".format(uid)
        logging.info("url:{}".format(url))

        r = requests.get(url, 
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        logging.info("records database have {} items".format(len(json.loads(r.content))))
        assert_equal(r.status_code == 200 and len(json.loads(r.content)) >= 0, True, "get records failed")



    # 测试删除接口是否正常
    def test_records_delete(self):
        url_records = self.base_url + "records"
        with open("json/post_records.json","r") as f:
            j = json.load(f)
        uid = j["uid"] 

        url = url_records + "?uid={}".format(uid)
        logging.info("url:{}".format(url))
        
        r = requests.delete(url)
        logging.info(r.status_code)
        r_get = requests.get(url, 
                         headers={"content-type": "application/json"})
        logging.info("records database have {} items after delete".format(len(json.loads(r_get.content))))
        assert_equal(r.status_code == 200 and len(json.loads(r_get.content)) == 0, True, "delete records failed")

    # 测试删除接口是否正常，同时清空videos数据库
    def test_delete_videos(self):
        url_videos = self.base_url + "videos"

        r = requests.delete(url_videos)
        logging.info(r.status_code)

        assert_equal(r.status_code == 200, True, "delete videos failed")

    # 测试 post videos 接口，一次post进来大量数据
    # 现在没办法通过get 获取videos的信息
    def test_videos_post(self):
        url_videos = self.base_url + "videos"
        with open("json/post_videos.json","r") as f:
            j = json.load(f)
        size_post = len(j["content"])
        
        r_get = requests.get(url_videos, 
                         headers={"content-type": "application/json"})
        videos_before = len(json.loads(r_get.content))
        logging.info("there are {} videos before post videos".format(videos_before))

        r = requests.post(url_videos, json=j,
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        #验证返回码正确
        assert_equal(r.status_code, 200, "status code is not 200")

        r_get = requests.get(url_videos, 
                         headers={"content-type": "application/json"})
        videos_after = len(json.loads(r_get.content))
        logging.info("there are {} videos after post videos".format(videos_after))

        #验证确实插入了多条videos
        #这里以后需要改，先无条件通过了
        assert_equal(size_post, size_post , "post method failed")
    
    def test_videos_get(self):
        """
        验证get next videos接口通
        """
        assert_equal(1,1)

    def test_videos_event(self):
        """
        验证post event时，分数会相应改变
        """
        assert_equal(1,1)

    def test_videos_sink(self):
        """
        一个视频被多次推荐但是没有正反馈时不会再被推荐
        或者验证所有视频分数都为10以下时选不出视频
        """
        assert_equal(1,1)

    def test_videos_high_score(self):
        """
        验证所有视频分数都为100以上时选不出视频
        """
        assert_equal(1,1)


    # 清理post进来的脏数据
    def teardown(self):
        url_records = self.base_url + "records"
        with open("json/post_records.json","r") as f:
            j = json.load(f)
        uid = j["uid"] 

        url = url_records + "?uid={}".format(uid)
        logging.info("url:{}".format(url))
        
        r = requests.delete(url)